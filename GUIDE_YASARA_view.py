# YASARA PLUGIN FOR DFT
# TOPIC:       SML
# TITLE:       SML
# AUTHOR:      A.sarkar # VERSION 4.1 extended
# LICENSE:     Non-Commercial
# DATE:        26.06.2023
# REVISION:    ORCA NMR/J-coupling, robust MOPAC UV-Vis selection, Mulliken Fukui and HTML reporting, 07.10.2026
# This is a YASARA plugin to be placed in the /plg subdirectory
# Interactive HTML uses the 3Dmol.js CDN for optimized structures and ORCA orbitals.
# Go to www.yasara.org/plugins for documentation and downloads

# YASARA menu entry
"""
MainMenu: GUIDE
  PullDownMenu : QM Calculation
    CustomWindow: QM Calculation
      Width: 600
      Height: 400
      TextInput:   X= 20,Y=50,Text="*Please insert the path of working folder",Width=150,Chars=150
      TextInput:   X= 20,Y=140,Text="*Please give a name of your project",Width=150,Chars=150
      List: X=360,Y=100,Text="METHODS"
        Width=200,Height=175,MultipleSelections=No
       Options=2, Text="ORCA"
                  Text="MOPAC"
      Button:    X=542,Y=348,Text="OK"
    Request: 
"""
class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

# importing essential modules
import yasara
import os
import sys
import platform
import time
import subprocess
import shutil
import re
import json
import base64
import html
import glob
import ast


def _dialog_value(value, index=0):
  """Return one YASARA dialog value without destroying spaces in paths."""
  if isinstance(value, (list, tuple)):
    if not value:
      return ''
    return str(value[index]).strip().strip('"').strip("'")

  raw_value = str(value).strip()
  if raw_value.startswith('[') and raw_value.endswith(']'):
    raw_value = raw_value[1:-1].strip()

  # A one-element ShowWin result is commonly represented as ['value'].
  if raw_value.startswith("'") and raw_value.endswith("'"):
    raw_value = raw_value[1:-1]
  elif raw_value.startswith('"') and raw_value.endswith('"'):
    raw_value = raw_value[1:-1]

  return raw_value.strip()


def _numeric_dialog_values(value):
  """Extract numeric values from a YASARA NumberInput dialog result."""
  if isinstance(value, (list, tuple)):
    raw_values = list(value)
  else:
    raw_values = re.findall(
      r'[-+]?\d*\.?\d+(?:[EeDd][-+]?\d+)?',
      str(value)
    )
  numbers = []
  for raw_value in raw_values:
    try:
      numbers.append(float(str(raw_value).strip()))
    except (TypeError, ValueError):
      continue
  return numbers


def _flatten_dialog_values(value):
  """Flatten nested YASARA ShowWin return values while preserving text."""
  if isinstance(value, (list, tuple)):
    flattened = []
    for item in value:
      flattened.extend(_flatten_dialog_values(item))
    return flattened

  if value is None:
    return []

  value_text = str(value).strip()
  if not value_text:
    return []

  if value_text[:1] in '[(' and value_text[-1:] in '])':
    try:
      parsed_value = ast.literal_eval(value_text)
    except (SyntaxError, ValueError):
      parsed_value = None
    if parsed_value is not None and parsed_value != value:
      return _flatten_dialog_values(parsed_value)

  return [value_text.strip().strip('"').strip("'")]


def _parse_mopac_dialog_result(value):
  """Return theory index, HF index and selected MOPAC calculation type."""
  flattened = _flatten_dialog_values(value)
  combined_text = ' '.join(flattened + [str(value)])
  normalized_text = combined_text.lower()
  normalized_text = normalized_text.replace('–', '-').replace('—', '-')
  normalized_text = re.sub(r'[_\s]+', ' ', normalized_text)

  method_patterns = (
    ('UV-Vis spectroscopy', (
      r'uv\s*-?\s*vis(?:ible)?\s+spectroscop',
      r'uvvis\s+spectroscop'
    )),
    ('Single-point', (r'single\s*-?\s*point',)),
    ('HOMO-LUMO', (r'homo\s*-?\s*lumo',)),
    ('Equilibrium-geometry', (r'equilibrium\s*-?\s*geometry',)),
    ('Import-job', (r'import\s*-?\s*job',))
  )

  methodology = ''
  for method_name, patterns in method_patterns:
    if any(re.search(pattern, normalized_text, re.IGNORECASE) for pattern in patterns):
      methodology = method_name
      break

  numeric_values = []
  for token in flattened:
    token_text = str(token).strip()
    if re.fullmatch(r'[-+]?\d+(?:\.0+)?', token_text):
      numeric_values.append(int(round(float(token_text))))

  if len(numeric_values) < 2:
    numeric_values = [
      int(round(float(number)))
      for number in re.findall(r'(?<![A-Za-z])[-+]?\d+(?:\.0+)?(?![A-Za-z])', str(value))
    ]

  theory_index = numeric_values[0] if len(numeric_values) > 0 else None
  hf_index = numeric_values[1] if len(numeric_values) > 1 else None

  # Some YASARA builds return the selected labels rather than radio indices.
  if theory_index is None:
    theory_name_map = {
      'AM1': 1,
      'PM3': 2,
      'PM6': 3,
      'PM7': 4,
      'RM1': 5,
      'MNDO': 6,
      'MNDOD': 7
    }
    upper_tokens = [str(token).strip().upper() for token in flattened]
    theory_index = next(
      (index for name, index in theory_name_map.items() if name in upper_tokens),
      None
    )

  if hf_index is None:
    upper_tokens = [str(token).strip().upper() for token in flattened]
    if 'RHF' in upper_tokens:
      hf_index = 1
    elif 'UHF' in upper_tokens:
      hf_index = 2

  if not methodology and len(numeric_values) > 2:
    method_index_map = {
      1: 'Single-point',
      2: 'HOMO-LUMO',
      3: 'Equilibrium-geometry',
      4: 'UV-Vis spectroscopy',
      5: 'Import-job'
    }
    for candidate in reversed(numeric_values[2:]):
      if candidate in method_index_map:
        methodology = method_index_map[candidate]
        break

  return theory_index, hf_index, methodology


def _read_path_file(path_file):
  """Read a stored path and repair paths corrupted by old newline handling."""
  with open(path_file, 'r', encoding='utf-8', errors='replace') as path_handle:
    path_parts = [line.strip() for line in path_handle if line.strip()]
  return ' '.join(path_parts).strip().strip('"').strip("'")


def _safe_remove(path, retries=5, delay=0.2):
  """Remove a temporary file without crashing if it is missing or briefly locked."""
  if not path:
    return True
  for attempt in range(retries):
    try:
      if os.path.exists(path):
        os.remove(path)
      return True
    except PermissionError:
      if attempt == retries - 1:
        print('WARNING: Could not remove locked file:', path)
        return False
      time.sleep(delay)
    except OSError as error:
      print('WARNING: Could not remove file:', path, error)
      return False
  return False


def _safe_move(source, destination, retries=5, delay=0.2):
  """Move/replace a file, with a copy fallback for Windows file-lock conflicts."""
  source = os.path.abspath(source)
  destination = os.path.abspath(destination)

  if source == destination:
    return destination
  if not os.path.isfile(source):
    raise FileNotFoundError('Source file does not exist: ' + source)

  os.makedirs(os.path.dirname(destination) or '.', exist_ok=True)
  _safe_remove(destination)

  for attempt in range(retries):
    try:
      os.replace(source, destination)
      return destination
    except PermissionError:
      if attempt < retries - 1:
        time.sleep(delay)
        continue
      break
    except OSError:
      break

  # Windows can deny rename/replace while another handle is still open.
  # Copying preserves the result and cleanup is attempted separately.
  shutil.copy2(source, destination)
  _safe_remove(source)
  return destination


def _resolve_executable(executable):
  """Resolve an absolute executable path or a command available on PATH."""
  executable_text = str(executable).strip().strip('"')
  if os.path.isfile(executable_text):
    return os.path.abspath(executable_text)
  resolved = shutil.which(executable_text)
  if resolved:
    return os.path.abspath(resolved)
  return os.path.abspath(executable_text)


def _run_executable(
  executable,
  arguments,
  workdir=None,
  stdout_path=None,
  stdin_text=None,
  environment=None,
  show_error=True
):
  """Run an external program without shell parsing or unquoted Windows paths."""
  executable = _resolve_executable(executable)
  if not os.path.isfile(executable):
    message = 'Executable was not found:\n' + executable
    if show_error:
      yasara.ShowMessage(message)
    raise FileNotFoundError(message)

  if workdir is None:
    workdir = os.getcwd()
  workdir = os.path.abspath(workdir)
  os.makedirs(workdir, exist_ok=True)

  command = [executable] + [str(argument) for argument in arguments]
  print('Running:', command)

  output_handle = None
  try:
    if stdout_path is not None:
      stdout_path = os.path.abspath(stdout_path)
      os.makedirs(os.path.dirname(stdout_path) or '.', exist_ok=True)
      output_handle = open(stdout_path, 'w', encoding='utf-8', errors='replace')

    result = subprocess.run(
      command,
      cwd=workdir,
      input=stdin_text,
      text=True if stdin_text is not None else False,
      stdout=output_handle,
      stderr=subprocess.STDOUT if output_handle is not None else None,
      shell=False,
      check=False,
      env=environment
    )
  finally:
    if output_handle is not None:
      output_handle.close()

  if result.returncode != 0:
    message = (
      'External calculation failed with return code ' +
      str(result.returncode) +
      '.\nPlease inspect the generated output file.'
    )
    print(message)
    if show_error:
      yasara.ShowMessage(message)

  return result.returncode


def _orca_terminated_normally(output_path):
  """Return True when an ORCA output contains its normal termination marker."""
  if not os.path.isfile(output_path):
    return False
  with open(output_path, 'r', encoding='utf-8', errors='replace') as handle:
    for line in handle:
      if 'ORCA TERMINATED NORMALLY' in line.upper():
        return True
  return False


def _run_orca(input_path, output_path):
  """Run ORCA and create an HTML/MO report when the main job is complete."""
  input_path = os.path.abspath(input_path)
  output_path = os.path.abspath(output_path)
  workdir = os.path.dirname(input_path) or os.getcwd()
  return_code = _run_executable(
    orca,
    [os.path.basename(input_path)],
    workdir=workdir,
    stdout_path=output_path
  )
  if return_code == 0 and not _orca_terminated_normally(output_path):
    print(
      'ORCA did not print its normal termination marker. '
      'The output file must be inspected before using the results.'
    )
    return 1
  if return_code == 0:
    try:
      _postprocess_orca_job(input_path, output_path)
    except Exception as report_error:
      print('WARNING: ORCA HTML post-processing failed:', report_error)
  return return_code


def _run_mopac(input_path):
  """Run MOPAC safely and create a generic HTML report when possible."""
  input_path = os.path.abspath(input_path)
  workdir = os.path.dirname(input_path) or os.getcwd()
  return_code = _run_executable(
    mopac,
    [os.path.basename(input_path)],
    workdir=workdir
  )
  if return_code == 0:
    try:
      _postprocess_mopac_job(input_path)
    except Exception as report_error:
      print('WARNING: MOPAC HTML post-processing failed:', report_error)
  return return_code


def _run_legacy_command(command):
  """Compatibility adapter for the original os.system-style command strings."""
  command = str(command).strip()
  left_command = command
  output_path = None

  if '>' in command:
    left_command, output_path = command.split('>', 1)
    left_command = left_command.strip()
    output_path = output_path.strip()

  orca_executable = globals().get('orca')
  if orca_executable and left_command.lower().startswith(str(orca_executable).lower()):
    input_path = left_command[len(str(orca_executable)):].strip().strip('"')
    if not os.path.isabs(input_path):
      input_path = os.path.join(os.getcwd(), input_path)
    if output_path is None:
      output_path = os.path.splitext(input_path)[0] + '.out'
    elif not os.path.isabs(output_path):
      output_path = os.path.join(os.getcwd(), output_path)
    return _run_orca(input_path, output_path)

  mopac_executable = globals().get('mopac')
  if mopac_executable and left_command.lower().startswith(str(mopac_executable).lower()):
    input_path = left_command[len(str(mopac_executable)):].strip().strip('"')
    if not os.path.isabs(input_path):
      input_path = os.path.join(os.getcwd(), input_path)
    return _run_mopac(input_path)

  # ORCA mapspc commands are handled here using the executable stored beside ORCA.
  lowered = left_command.lower()
  if lowered.startswith('orca_mapspc.exe ') or lowered.startswith('./orca_mapspc ') or lowered.startswith('orca_mapspc '):
    executable_name = 'orca_mapspc.exe' if platform.system() == 'Windows' else 'orca_mapspc'
    executable_path = os.path.join(os.getcwd(), executable_name)
    executable_token = left_command.split(None, 1)[0]
    remainder = left_command[len(executable_token):].strip()
    if ' ABS ' in remainder:
      spectrum_file, option_text = remainder.split(' ABS ', 1)
      arguments = [spectrum_file.strip().strip('"'), 'ABS'] + option_text.split()
    else:
      arguments = remainder.split()
    return _run_executable(executable_path, arguments, workdir=os.getcwd())

  # Last-resort fallback for commands unrelated to ORCA/MOPAC.
  print('WARNING: Falling back to shell command:', command)
  return subprocess.run(command, shell=True, check=False).returncode


def _require_molecule_from_smiles(smiles_text):
  """Parse SMILES and stop the plugin with a clear message on failure."""
  molecule = Chem.MolFromSmiles(str(smiles_text).strip())
  if molecule is None:
    message = 'RDKit could not parse the SMILES generated by YASARA.'
    yasara.ShowMessage(message)
    raise ValueError(message)
  return molecule


def _parse_last_orbital_table(output_path):
  """Parse the last ORCA ORBITAL ENERGIES table."""
  with open(output_path, 'r', encoding='utf-8', errors='replace') as handle:
    lines = handle.readlines()

  section_starts = [
    index for index, line in enumerate(lines)
    if 'ORBITAL ENERGIES' in line.upper()
  ]
  if not section_starts:
    raise ValueError('No ORBITAL ENERGIES section was found in: ' + output_path)

  row_pattern = re.compile(
    r'^\s*(\d+)\s+'
    r'([-+]?\d*\.?\d+(?:[EeDd][-+]?\d+)?)\s+'
    r'([-+]?\d*\.?\d+(?:[EeDd][-+]?\d+)?)\s+'
    r'([-+]?\d*\.?\d+(?:[EeDd][-+]?\d+)?)'
  )

  orbital_rows = []
  started = False
  for line in lines[section_starts[-1] + 1:]:
    match = row_pattern.match(line)
    if match:
      started = True
      orbital_rows.append({
        'number': int(match.group(1)),
        'occupation': float(match.group(2).replace('D', 'E').replace('d', 'e')),
        'energy_eh': float(match.group(3).replace('D', 'E').replace('d', 'e')),
        'energy_ev': float(match.group(4).replace('D', 'E').replace('d', 'e'))
      })
    elif started:
      break

  if not orbital_rows:
    raise ValueError('The ORBITAL ENERGIES table contained no readable rows: ' + output_path)
  return orbital_rows


def _save_homo_lumo_results(output_path, file_prefix):
  """Calculate and save HOMO/LUMO energies from an ORCA output file."""
  orbital_rows = _parse_last_orbital_table(output_path)
  occupied = [row for row in orbital_rows if row['occupation'] > 1.0e-6]
  unoccupied = [row for row in orbital_rows if row['occupation'] <= 1.0e-6]

  if not occupied or not unoccupied:
    raise ValueError('Occupied or unoccupied orbital rows are missing in: ' + output_path)

  homo = max(occupied, key=lambda row: row['energy_ev'])
  possible_lumos = [row for row in unoccupied if row['energy_ev'] > homo['energy_ev']]
  lumo = min(possible_lumos or unoccupied, key=lambda row: row['energy_ev'])
  gap_ev = lumo['energy_ev'] - homo['energy_ev']
  gap_eh = lumo['energy_eh'] - homo['energy_eh']

  final_file = file_prefix + '_orbital_energy_final.txt'
  dat_file = file_prefix + '_orbital_energy_dat.txt'
  homo_lumo_file = file_prefix + '_HOMO_lumo_ev.txt'

  with open(final_file, 'w', encoding='utf-8') as handle:
    handle.write('NO\tOCC\tE(Eh)\tE(eV)\n')
    for row in orbital_rows:
      handle.write('{0}\t{1:.4f}\t{2:.10f}\t{3:.10f}\n'.format(
        row['number'], row['occupation'], row['energy_eh'], row['energy_ev']
      ))

  with open(dat_file, 'w', encoding='utf-8') as handle:
    for row in orbital_rows:
      handle.write('{0:.4f}\t{1:.10f}\t{2:.10f}\n'.format(
        row['occupation'], row['energy_eh'], row['energy_ev']
      ))

  with open(homo_lumo_file, 'w', encoding='utf-8') as handle:
    handle.write('HOMO\t{0}\t{1:.10f}\t{2:.10f}\n'.format(
      homo['number'], homo['energy_eh'], homo['energy_ev']
    ))
    handle.write('LUMO\t{0}\t{1:.10f}\t{2:.10f}\n'.format(
      lumo['number'], lumo['energy_eh'], lumo['energy_ev']
    ))

  return homo, lumo, gap_eh, gap_ev


def _extract_final_scf_energy(output_path):
  """Return the final ORCA electronic energy in Hartree."""
  final_energy = None
  energy_patterns = (
    re.compile(r'FINAL SINGLE POINT ENERGY\s+([-+]?\d*\.?\d+(?:[EeDd][-+]?\d+)?)'),
    re.compile(r'SCF[_ ]ENERGY\s*[:=]?\s*([-+]?\d*\.?\d+(?:[EeDd][-+]?\d+)?)', re.IGNORECASE)
  )

  with open(output_path, 'r', encoding='utf-8', errors='replace') as handle:
    for line in handle:
      for pattern in energy_patterns:
        match = pattern.search(line)
        if match:
          final_energy = float(match.group(1).replace('D', 'E').replace('d', 'e'))

  if final_energy is None:
    raise ValueError('No final SCF energy was found in: ' + output_path)
  return final_energy


def _parse_last_hirshfeld_table(output_path):
  """Parse the final ORCA HIRSHFELD ANALYSIS atom-charge table."""
  with open(output_path, 'r', encoding='utf-8', errors='replace') as handle:
    lines = handle.readlines()

  section_starts = [
    index for index, line in enumerate(lines)
    if 'HIRSHFELD ANALYSIS' in line.upper()
  ]
  if not section_starts:
    raise ValueError('No HIRSHFELD ANALYSIS section was found in: ' + output_path)

  row_pattern = re.compile(
    r'^\s*(\d+)\s+([A-Za-z][A-Za-z0-9]*)\s+'
    r'([-+]?\d*\.?\d+(?:[EeDd][-+]?\d+)?)'
    r'(?:\s+[-+]?\d*\.?\d+(?:[EeDd][-+]?\d+)?)?\s*$'
  )

  rows = []
  started = False
  for line in lines[section_starts[-1] + 1:]:
    match = row_pattern.match(line)
    if match:
      started = True
      rows.append({
        'index': int(match.group(1)),
        'element': match.group(2),
        'charge': float(match.group(3).replace('D', 'E').replace('d', 'e'))
      })
    elif started and (not line.strip() or 'TOTAL' in line.upper() or 'TIMINGS' in line.upper()):
      break

  if not rows:
    raise ValueError('The Hirshfeld section contained no readable atom rows: ' + output_path)
  return rows


def _parse_last_mulliken_table(output_path):
  """Parse the final ORCA Mulliken atomic-charge table."""
  with open(output_path, 'r', encoding='utf-8', errors='replace') as handle:
    lines = handle.readlines()

  section_starts = [
    index for index, line in enumerate(lines)
    if (
      'MULLIKEN ATOMIC CHARGES' in line.upper() or
      'MULLIKEN ATOMIC CHARGES AND SPIN POPULATIONS' in line.upper()
    )
  ]
  if not section_starts:
    raise ValueError(
      'No MULLIKEN ATOMIC CHARGES section was found in: ' + output_path
    )

  row_patterns = (
    re.compile(
      r'^\s*(\d+)\s+([A-Za-z][A-Za-z0-9]*)\s*:\s*'
      r'([-+]?\d*\.?\d+(?:[EeDd][-+]?\d+)?)'
    ),
    re.compile(
      r'^\s*(\d+)\s+([A-Za-z][A-Za-z0-9]*)\s+'
      r'([-+]?\d*\.?\d+(?:[EeDd][-+]?\d+)?)'
      r'(?:\s+[-+]?\d*\.?\d+(?:[EeDd][-+]?\d+)?)?\s*$'
    )
  )

  rows = []
  started = False
  for line in lines[section_starts[-1] + 1:]:
    match = None
    for row_pattern in row_patterns:
      match = row_pattern.match(line)
      if match:
        break

    if match:
      started = True
      rows.append({
        'index': int(match.group(1)),
        'element': match.group(2),
        'charge': float(match.group(3).replace('D', 'E').replace('d', 'e'))
      })
    elif started and (
      not line.strip() or
      'SUM OF ATOMIC CHARGES' in line.upper() or
      'MULLIKEN REDUCED' in line.upper() or
      'LOEWDIN' in line.upper() or
      'TIMINGS' in line.upper()
    ):
      break

  if not rows:
    raise ValueError(
      'The Mulliken section contained no readable atom rows: ' + output_path
    )
  return rows


def _save_fukui_results(
  neutral_output,
  cation_output,
  anion_output,
  file_prefix,
  population_scheme='mulliken'
):
  """Calculate radical condensed Fukui values from ORCA atomic charges."""
  scheme = str(population_scheme).strip().lower()
  if scheme == 'hirshfeld':
    parser = _parse_last_hirshfeld_table
    scheme_label = 'Hirshfeld'
    file_label = 'hirshfeld'
  elif scheme == 'mulliken':
    parser = _parse_last_mulliken_table
    scheme_label = 'Mulliken'
    file_label = 'mulliken'
  else:
    raise ValueError('Unsupported Fukui population scheme: ' + str(population_scheme))

  neutral_rows = parser(neutral_output)
  cation_rows = parser(cation_output)
  anion_rows = parser(anion_output)

  if not (len(neutral_rows) == len(cation_rows) == len(anion_rows)):
    raise ValueError(
      'Neutral, cation and anion ' + scheme_label +
      ' tables have different atom counts.'
    )

  result_rows = []
  for neutral, cation, anion in zip(neutral_rows, cation_rows, anion_rows):
    if neutral['index'] != cation['index'] or neutral['index'] != anion['index']:
      raise ValueError('Atom indices differ between the ' + scheme_label + ' tables.')
    if neutral['element'] != cation['element'] or neutral['element'] != anion['element']:
      raise ValueError('Atom elements differ between the ' + scheme_label + ' tables.')

    radical_fukui = round((anion['charge'] - cation['charge']) / 2.0, 3)
    result_rows.append({
      'index': neutral['index'],
      'element': neutral['element'],
      'neutral_charge': neutral['charge'],
      'cation_charge': cation['charge'],
      'anion_charge': anion['charge'],
      'fukui': radical_fukui
    })

  for state_name, charge_key in (
    ('initial', 'neutral_charge'),
    ('cation', 'cation_charge'),
    ('anion', 'anion_charge')
  ):
    charge_path = file_prefix + '_' + state_name + '_' + file_label + '_charge.txt'
    with open(charge_path, 'w', encoding='utf-8') as handle:
      for row in result_rows:
        handle.write('{0:.10f}\n'.format(row[charge_key]))

  results_path = file_prefix + '_fukuifunction_results.txt'
  with open(results_path, 'w', encoding='utf-8') as handle:
    handle.write('POPULATION_SCHEME\t' + scheme_label + '\n')
    handle.write('ATOM\tELEMENT\tRADICAL_FUKUI\n')
    for row in result_rows:
      handle.write('{0}\t{1}\t{2:.3f}\n'.format(
        row['index'] + 1,
        row['element'],
        row['fukui']
      ))

  for display_index, row in enumerate(result_rows, start=1):
    fukui_text = str(row['fukui'])
    yasara.run('ZoomAll Steps=10')
    yasara.run(
      'LabelAtom ' + str(display_index) +
      ',Format=' + fukui_text +
      ',Height=0.2,Color=Black,X=0.0,Y=0.0,Z=0.0'
    )
    yasara.run('BFactorAtom ' + str(display_index) + ',' + fukui_text)

  return result_rows, results_path

_ATOMIC_NUMBERS = {
  'H': 1, 'HE': 2, 'LI': 3, 'BE': 4, 'B': 5, 'C': 6, 'N': 7,
  'O': 8, 'F': 9, 'NE': 10, 'NA': 11, 'MG': 12, 'AL': 13,
  'SI': 14, 'P': 15, 'S': 16, 'CL': 17, 'AR': 18, 'BR': 35, 'I': 53
}

_NMR_LABELS = {
  1: '1H', 6: '13C', 7: '15N', 9: '19F', 15: '31P'
}

# Approximate Larmor-frequency ratios relative to 1H at the same field.
_NMR_FREQUENCY_RATIOS = {
  1: 1.0,
  6: 0.25145,
  7: 0.10137,
  9: 0.94094,
  15: 0.40481
}


def _read_text(path):
  if not path or not os.path.isfile(path):
    return ''
  with open(path, 'r', encoding='utf-8', errors='replace') as handle:
    return handle.read()


def _image_data_uri(path):
  if not path or not os.path.isfile(path):
    return ''
  extension = os.path.splitext(path)[1].lower()
  mime = 'image/png' if extension == '.png' else 'image/jpeg'
  with open(path, 'rb') as handle:
    encoded = base64.b64encode(handle.read()).decode('ascii')
  return 'data:' + mime + ';base64,' + encoded


def _extract_xyz_from_orca_input(input_path, output_xyz):
  """Extract inline ORCA XYZ coordinates or copy an XYZFILE target."""
  if not os.path.isfile(input_path):
    return None
  with open(input_path, 'r', encoding='utf-8', errors='replace') as handle:
    lines = handle.readlines()

  for line in lines:
    match = re.match(r'^\s*\*\s*xyzfile\s+[-+]?\d+\s+\d+\s+(.+?)\s*$', line, re.IGNORECASE)
    if match:
      xyz_name = match.group(1).strip().strip('"').strip("'")
      xyz_path = xyz_name if os.path.isabs(xyz_name) else os.path.join(os.path.dirname(input_path), xyz_name)
      if os.path.isfile(xyz_path):
        shutil.copy2(xyz_path, output_xyz)
        return output_xyz

  start_index = None
  for index, line in enumerate(lines):
    if re.match(r'^\s*\*\s*xyz\s+[-+]?\d+\s+\d+', line, re.IGNORECASE):
      start_index = index + 1
      break
  if start_index is None:
    return None

  coordinates = []
  for line in lines[start_index:]:
    if line.strip().startswith('*'):
      break
    tokens = line.split()
    if len(tokens) >= 4:
      try:
        float(tokens[1])
        float(tokens[2])
        float(tokens[3])
      except ValueError:
        continue
      coordinates.append(' '.join(tokens[:4]))

  if not coordinates:
    return None
  with open(output_xyz, 'w', encoding='utf-8') as handle:
    handle.write(str(len(coordinates)) + '\n')
    handle.write('Coordinates extracted from ORCA input\n')
    handle.write('\n'.join(coordinates) + '\n')
  return output_xyz


def _find_structure_file(base_prefix, input_path=None):
  candidates = [
    base_prefix + '.xyz',
    base_prefix + '_optimized.xyz',
    base_prefix + '.opt.xyz',
    base_prefix + '_trj.xyz'
  ]
  for candidate in candidates:
    if os.path.isfile(candidate) and os.path.getsize(candidate) > 0:
      return candidate
  if input_path:
    extracted = base_prefix + '_input.xyz'
    return _extract_xyz_from_orca_input(input_path, extracted)
  return None


def _parse_orca_method_details(input_path):
  """Extract useful calculation metadata from an ORCA input file."""
  details = {}
  if not input_path or not os.path.isfile(input_path):
    return details

  keyword_tokens = []
  charge_multiplicity_pattern = re.compile(
    r'^\s*\*\s*xyz(?:file)?\s+([-+]?\d+)\s+(\d+)',
    re.IGNORECASE
  )
  with open(input_path, 'r', encoding='utf-8', errors='replace') as handle:
    for line in handle:
      if line.lstrip().startswith('!') and not keyword_tokens:
        keywords = line.lstrip()[1:].strip()
        details['ORCA keywords'] = keywords
        keyword_tokens = keywords.split()
      coordinate_match = charge_multiplicity_pattern.match(line)
      if coordinate_match:
        details['Charge'] = coordinate_match.group(1)
        details['Multiplicity'] = coordinate_match.group(2)

  control_keywords = {
    'SP', 'OPT', 'FREQ', 'NUMFREQ', 'NMR', 'KEEPDENS', 'TIGHTSCF',
    'NEB-TS', 'TDDFT', 'HIRSHFELD', 'GRID6', 'DEFGRID3', 'AUTOAUX',
    'QM/MM', 'QM/QM2', 'QM/XTB', 'CPCM', 'NOFROZENCORE'
  }
  basis_markers = (
    'DEF2', 'MA-DEF2', '6-31', 'CC-PV', 'AUG-CC', 'PCSSEG', 'PCJ',
    'SVP', 'TZVP', 'QZVP', 'STO-3G'
  )
  method_token = None
  basis_token = None
  for token in keyword_tokens:
    upper = token.upper()
    if upper in control_keywords or upper.startswith('CPCM('):
      continue
    if any(marker in upper for marker in basis_markers):
      if basis_token is None:
        basis_token = token
      continue
    if method_token is None:
      method_token = token

  if method_token is not None:
    details['Method'] = method_token
  if basis_token is not None:
    details['Basis'] = basis_token
  return details


def _generate_orca_mo_cube(base_prefix, orbital_number, label):
  """Generate one ORCA MO cube by driving orca_plot in interactive mode."""
  if orbital_number is None or not os.path.isfile(base_prefix + '.gbw'):
    return None
  executable_name = 'orca_plot.exe' if platform.system() == 'Windows' else 'orca_plot'
  executable_path = os.path.join(globals().get('orcap', ''), executable_name)
  if not os.path.isfile(executable_path):
    executable_path = shutil.which(executable_name) or executable_path
  if not os.path.isfile(executable_path):
    print('WARNING: orca_plot was not found; MO cube generation was skipped.')
    return None

  workdir = os.path.dirname(base_prefix) or os.getcwd()
  gbw_name = os.path.basename(base_prefix) + '.gbw'
  interaction = (
    '2\n' + str(orbital_number) + '\n'
    '3\n0\n'
    '4\n60\n'
    '5\n7\n'
    '8\n0\n'
    '11\n12\n'
  )
  log_path = base_prefix + '_' + label.lower() + '_orca_plot.log'
  return_code = _run_executable(
    executable_path,
    [gbw_name, '-i'],
    workdir=workdir,
    stdout_path=log_path,
    stdin_text=interaction,
    show_error=False
  )
  if return_code != 0:
    return None

  expected = base_prefix + '.mo' + str(orbital_number) + 'a.cube'
  if os.path.isfile(expected):
    named = base_prefix + '_' + label.upper() + '.cube'
    shutil.copy2(expected, named)
    return named

  pattern = os.path.join(workdir, os.path.basename(base_prefix) + '.mo' + str(orbital_number) + '*.cube')
  matches = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
  if matches:
    named = base_prefix + '_' + label.upper() + '.cube'
    shutil.copy2(matches[0], named)
    return named
  return None


def _parse_nmr_shieldings(output_path):
  """Parse the final ORCA isotropic shielding table in ppm."""
  with open(output_path, 'r', encoding='utf-8', errors='replace') as handle:
    lines = handle.readlines()

  # ORCA prints a compact summary table at the end of every shielding section.
  # Prefer the last summary because post-HF or multi-step jobs can print several.
  summary_tables = []
  summary_header = re.compile(
    r'^\s*Nucleus\s+Element\s+Isotropic\s+Anisotropy',
    re.IGNORECASE
  )
  summary_row = re.compile(
    r'^\s*(\d+)\s+([A-Za-z]+)\s+'
    r'([-+]?\d*\.?\d+(?:[EeDd][-+]?\d+)?)'
    r'(?:\s+[-+]?\d*\.?\d+(?:[EeDd][-+]?\d+)?)?\s*$'
  )

  for header_index, line in enumerate(lines):
    if not summary_header.search(line):
      continue
    table = []
    started = False
    for candidate in lines[header_index + 1:]:
      match = summary_row.match(candidate)
      if match:
        started = True
        table.append({
          'index': int(match.group(1)),
          'element': match.group(2).capitalize(),
          'shielding_ppm': float(
            match.group(3).replace('D', 'E').replace('d', 'e')
          )
        })
      elif started:
        break
    if table:
      summary_tables.append(table)

  if summary_tables:
    return summary_tables[-1]

  # Fallback for older ORCA versions: parse each detailed nucleus block.
  results = []
  current = None
  nucleus_pattern = re.compile(
    r'^\s*Nucleus\s+(\d+)\s*([A-Za-z]+)\s*:',
    re.IGNORECASE
  )
  iso_pattern = re.compile(
    r'^\s*Total\s+.*?iso\s*=\s*'
    r'([-+]?\d*\.?\d+(?:[EeDd][-+]?\d+)?)',
    re.IGNORECASE
  )
  for line in lines:
    nucleus_match = nucleus_pattern.search(line)
    if nucleus_match:
      current = {
        'index': int(nucleus_match.group(1)),
        'element': nucleus_match.group(2).capitalize()
      }
      continue
    if current is not None:
      iso_match = iso_pattern.search(line)
      if iso_match:
        record = dict(current)
        record['shielding_ppm'] = float(
          iso_match.group(1).replace('D', 'E').replace('d', 'e')
        )
        results.append(record)
        current = None

  final = {}
  for row in results:
    final[(row['index'], row['element'])] = row
  parsed = [final[key] for key in sorted(final)]
  if not parsed:
    raise ValueError(
      'No ORCA isotropic NMR shielding table was found in: ' + output_path
    )
  return parsed


def _parse_j_coupling_matrix(output_path):
  """Parse ORCA's block-formatted isotropic J-coupling matrix in Hz."""
  with open(output_path, 'r', encoding='utf-8', errors='replace') as handle:
    lines = handle.readlines()
  start = None
  for index, line in enumerate(lines):
    if 'SUMMARY OF ISOTROPIC COUPLING CONSTANTS J' in line.upper():
      start = index + 1
  if start is None:
    return {}, {}

  labels = {}
  matrix = {}
  current_columns = []
  header_pattern = re.compile(r'(\d+)\s+([A-Za-z]+)')
  row_pattern = re.compile(r'^\s*(\d+)\s+([A-Za-z]+)\s+(.+)$')
  numeric_pattern = re.compile(r'[-+]?\d*\.\d+(?:[EeDd][-+]?\d+)?|[-+]?\d+(?:[EeDd][-+]?\d+)')
  blank_count = 0

  for line in lines[start:]:
    upper = line.upper()
    if 'TIMINGS' in upper or 'NMR CHEMICAL' in upper or 'ORCA TERMINATED' in upper:
      break
    if not line.strip():
      blank_count += 1
      if blank_count > 5 and matrix:
        break
      continue
    blank_count = 0
    if set(line.strip()) <= {'-'}:
      continue

    pairs = [(int(number), element.capitalize()) for number, element in header_pattern.findall(line)]
    # Column headers consist only of repeated atom-index/element pairs and no decimals.
    if pairs and not re.search(r'[-+]?\d+\.\d+', line):
      current_columns = pairs
      continue

    row_match = row_pattern.match(line)
    if row_match and current_columns:
      row_index = int(row_match.group(1))
      row_element = row_match.group(2).capitalize()
      values = [float(value.replace('D', 'E').replace('d', 'e')) for value in numeric_pattern.findall(row_match.group(3))]
      if values:
        labels[row_index] = row_element
        matrix.setdefault(row_index, {})
        for column, value in zip(current_columns, values):
          column_index, column_element = column
          labels[column_index] = column_element
          matrix[row_index][column_index] = value
          matrix.setdefault(column_index, {})[row_index] = value
        continue

  return labels, matrix


def _write_j_coupling_csv(path, labels, matrix):
  indices = sorted(set(labels) | set(matrix))
  with open(path, 'w', encoding='utf-8', newline='') as handle:
    writer = csv.writer(handle)
    writer.writerow(['Atom'] + [str(index + 1) + labels.get(index, '') for index in indices])
    for row_index in indices:
      writer.writerow(
        [str(row_index + 1) + labels.get(row_index, '')] +
        [matrix.get(row_index, {}).get(column_index, 0.0) for column_index in indices]
      )
  return path


def _parse_nmrspectrum_peaks(output_path):
  """Parse spin-Hamiltonian peaks generated by ORCA orca_nmrspectrum."""
  peaks = {}
  current_atomic_number = None
  section_pattern = re.compile(r'NMR Peaks for atom type\s+(\d+)', re.IGNORECASE)
  row_pattern = re.compile(r'^\s*(\d+)\s+([-+]?\d*\.?\d+)\s+([-+]?\d*\.?\d+)\s*$')
  with open(output_path, 'r', encoding='utf-8', errors='replace') as handle:
    for line in handle:
      section_match = section_pattern.search(line)
      if section_match:
        current_atomic_number = int(section_match.group(1))
        peaks.setdefault(current_atomic_number, [])
        continue
      if current_atomic_number is not None:
        row_match = row_pattern.match(line)
        if row_match:
          peaks[current_atomic_number].append({
            'atom': int(row_match.group(1)),
            'shift_ppm': float(row_match.group(2)),
            'intensity': float(row_match.group(3))
          })
  return {number: rows for number, rows in peaks.items() if rows}


def _coalesce_nmr_lines(lines, tolerance_ppm):
  if not lines:
    return []
  lines = sorted(lines, key=lambda item: item[0])
  merged = []
  for shift, intensity in lines:
    if merged and abs(shift - merged[-1][0]) <= tolerance_ppm:
      old_shift, old_intensity = merged[-1]
      total_intensity = old_intensity + intensity
      weighted_shift = (old_shift * old_intensity + shift * intensity) / total_intensity
      merged[-1] = (weighted_shift, total_intensity)
    else:
      merged.append((shift, intensity))
  return merged


def _simulate_first_order_nmr(shieldings, labels, matrix, frequency_mhz, references):
  """Fallback first-order spectrum using shielding shifts and the parsed J matrix."""
  peaks = {}
  atoms_by_index = {row['index']: row for row in shieldings}
  for row in shieldings:
    atomic_number = _ATOMIC_NUMBERS.get(row['element'].upper())
    if atomic_number not in references:
      continue
    center = references[atomic_number] - row['shielding_ppm']
    nucleus_frequency_mhz = (
      float(frequency_mhz) * _NMR_FREQUENCY_RATIOS.get(atomic_number, 1.0)
    )
    lines = [(center, 1.0)]
    couplings = []
    for partner, value in matrix.get(row['index'], {}).items():
      if partner == row['index'] or partner not in atoms_by_index:
        continue
      if abs(value) >= 0.3:
        couplings.append(abs(value))
    for coupling_hz in sorted(couplings, reverse=True)[:8]:
      half_split_ppm = coupling_hz / (2.0 * max(nucleus_frequency_mhz, 1.0e-9))
      split_lines = []
      for shift, intensity in lines:
        split_lines.append((shift - half_split_ppm, intensity / 2.0))
        split_lines.append((shift + half_split_ppm, intensity / 2.0))
      lines = _coalesce_nmr_lines(
        split_lines,
        0.2 / max(nucleus_frequency_mhz, 1.0e-9)
      )
    peaks.setdefault(atomic_number, [])
    for shift, intensity in lines:
      peaks[atomic_number].append({
        'atom': row['index'],
        'shift_ppm': shift,
        'intensity': intensity
      })
  return peaks


def _create_nmr_plots(peaks_by_atomic_number, base_prefix, frequency_mhz, linewidth_hz=1.0):
  """Create broadened, reversed-axis NMR plots from J-resolved peak lists."""
  image_paths = []
  for atomic_number, peaks in sorted(peaks_by_atomic_number.items()):
    if not peaks:
      continue
    shifts = np.array([row['shift_ppm'] for row in peaks], dtype=float)
    intensities = np.array([row['intensity'] for row in peaks], dtype=float)
    margin = max(0.5, (float(shifts.max()) - float(shifts.min())) * 0.08)
    x_values = np.linspace(float(shifts.min()) - margin, float(shifts.max()) + margin, 5000)
    nucleus_frequency_mhz = (
      float(frequency_mhz) * _NMR_FREQUENCY_RATIOS.get(atomic_number, 1.0)
    )
    gamma_ppm = max(
      linewidth_hz / max(nucleus_frequency_mhz, 1.0e-9),
      0.001
    ) / 2.0
    spectrum = np.zeros_like(x_values)
    for shift, intensity in zip(shifts, intensities):
      spectrum += intensity * (gamma_ppm ** 2) / ((x_values - shift) ** 2 + gamma_ppm ** 2)
    if spectrum.max() > 0:
      spectrum /= spectrum.max()

    label = _NMR_LABELS.get(atomic_number, str(atomic_number) + 'X')
    image_path = base_prefix + '_' + label + '_NMR.png'
    plt.figure(figsize=(10, 4.8))
    plt.plot(x_values, spectrum)
    plt.gca().invert_xaxis()
    plt.xlabel('Chemical shift (ppm)')
    plt.ylabel('Relative intensity')
    plt.title(
      label + ' NMR spectrum at ' +
      str(round(nucleus_frequency_mhz, 2)) + ' MHz'
    )
    plt.ylim(bottom=0)
    plt.tight_layout()
    plt.savefig(image_path, dpi=180)
    plt.close()
    image_paths.append(image_path)
  return image_paths


def _write_nmr_peak_csv(path, peaks_by_atomic_number):
  with open(path, 'w', encoding='utf-8', newline='') as handle:
    writer = csv.writer(handle)
    writer.writerow(['Nucleus', 'Atom', 'Shift_ppm', 'Relative_intensity'])
    for atomic_number, peaks in sorted(peaks_by_atomic_number.items()):
      label = _NMR_LABELS.get(atomic_number, str(atomic_number))
      for peak in peaks:
        writer.writerow([label, peak['atom'] + 1, peak['shift_ppm'], peak['intensity']])
  return path


def _generate_html_report(
  base_prefix,
  engine,
  details,
  xyz_path=None,
  homo_cube=None,
  lumo_cube=None,
  image_paths=None,
  data_files=None,
  nmr_peaks=None,
  j_labels=None,
  j_matrix=None
):
  """Create a results page with a 3Dmol.js orbital viewer."""
  image_paths = image_paths or []
  data_files = data_files or []
  nmr_peaks = nmr_peaks or {}
  j_labels = j_labels or {}
  j_matrix = j_matrix or {}

  xyz_data = _read_text(xyz_path)
  homo_data = _read_text(homo_cube)
  lumo_data = _read_text(lumo_cube)
  report_path = base_prefix + '_DFT_report.html'
  report_dir = os.path.dirname(report_path) or os.getcwd()

  detail_rows = []
  for key, value in details.items():
    if value is None:
      continue
    detail_rows.append(
      '<tr><th>' + html.escape(str(key)) + '</th><td>' + html.escape(str(value)) + '</td></tr>'
    )

  file_links = []
  for file_path in data_files:
    if file_path and os.path.isfile(file_path):
      relative = os.path.relpath(file_path, report_dir).replace('\\', '/')
      file_links.append('<li><a href="' + html.escape(relative) + '">' + html.escape(os.path.basename(file_path)) + '</a></li>')

  image_html = []
  for image_path in image_paths:
    uri = _image_data_uri(image_path)
    if uri:
      image_html.append(
        '<section class="panel"><h2>' + html.escape(os.path.basename(image_path)) +
        '</h2><img class="spectrum" src="' + uri + '" alt="Spectrum"></section>'
      )

  peak_rows = []
  for atomic_number, peaks in sorted(nmr_peaks.items()):
    nucleus = _NMR_LABELS.get(atomic_number, str(atomic_number))
    for peak in peaks:
      peak_rows.append(
        '<tr><td>' + html.escape(nucleus) + '</td><td>' + str(peak['atom'] + 1) +
        '</td><td>' + format(peak['shift_ppm'], '.5f') + '</td><td>' +
        format(peak['intensity'], '.5f') + '</td></tr>'
      )
  peak_table = ''
  if peak_rows:
    peak_table = (
      '<section class="panel"><h2>J-resolved NMR peaks</h2><div class="scroll"><table>'
      '<tr><th>Nucleus</th><th>Atom</th><th>Shift (ppm)</th><th>Relative intensity</th></tr>' +
      ''.join(peak_rows) + '</table></div></section>'
    )

  j_table = ''
  j_indices = sorted(set(j_labels) | set(j_matrix))
  if j_indices:
    header = ''.join('<th>' + str(index + 1) + html.escape(j_labels.get(index, '')) + '</th>' for index in j_indices)
    body = []
    for row_index in j_indices:
      cells = ''.join(
        '<td>' + format(j_matrix.get(row_index, {}).get(column_index, 0.0), '.3f') + '</td>'
        for column_index in j_indices
      )
      body.append('<tr><th>' + str(row_index + 1) + html.escape(j_labels.get(row_index, '')) + '</th>' + cells + '</tr>')
    j_table = (
      '<section class="panel"><h2>Isotropic J-coupling matrix (Hz)</h2><div class="scroll"><table>'
      '<tr><th>Atom</th>' + header + '</tr>' + ''.join(body) + '</table></div></section>'
    )

  viewer_section = ''
  if xyz_data:
    has_orbitals = bool(homo_data or lumo_data)
    viewer_title = (
      'Interactive optimized molecular-orbital view'
      if has_orbitals else
      'Interactive optimized molecular structure'
    )
    viewer_note = (
      'Blue and red surfaces represent positive and negative orbital phases. '
      if has_orbitals else
      'No volumetric molecular-orbital cube was generated for this calculation. '
    )
    viewer_section = '''
    <section class="panel">
      <h2>''' + html.escape(viewer_title) + '''</h2>
      <div class="toolbar">
        <button onclick="showStructure()">Structure</button>
        <button onclick="showOrbital('homo')" id="homoButton">HOMO</button>
        <button onclick="showOrbital('lumo')" id="lumoButton">LUMO</button>
      </div>
      <div id="viewer"></div>
      <p class="note">''' + html.escape(viewer_note) + '''The viewer loads 3Dmol.js from its public CDN, so opening this HTML requires internet access.</p>
    </section>
    '''

  document = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GUIDE quantum chemistry report</title>
<script src="https://3Dmol.org/build/3Dmol-min.js"></script>
<style>
  body { font-family: Arial, sans-serif; margin: 0; background: #f3f5f7; color: #1c2733; }
  header { padding: 24px 30px; background: #182533; color: white; }
  main { max-width: 1180px; margin: 22px auto; padding: 0 18px 40px; }
  .panel { background: white; border-radius: 10px; padding: 20px; margin-bottom: 18px; box-shadow: 0 2px 10px rgba(0,0,0,.08); }
  table { border-collapse: collapse; width: 100%; }
  th, td { border: 1px solid #dce2e7; padding: 7px 9px; text-align: left; white-space: nowrap; }
  th { background: #eef2f5; }
  #viewer { width: 100%; height: 620px; position: relative; border: 1px solid #dce2e7; border-radius: 8px; }
  .toolbar { margin-bottom: 10px; }
  button { padding: 8px 15px; margin-right: 8px; cursor: pointer; }
  .spectrum { width: 100%; max-height: 580px; object-fit: contain; }
  .scroll { overflow: auto; max-height: 540px; }
  .note { color: #556270; font-size: 0.9rem; }
</style>
</head>
<body>
<header><h1>GUIDE quantum chemistry calculation report</h1><div>Engine: ''' + html.escape(str(engine)) + '''</div></header>
<main>
<section class="panel"><h2>Calculation details</h2><table>''' + ''.join(detail_rows) + '''</table></section>
''' + viewer_section + ''.join(image_html) + peak_table + j_table + '''
<section class="panel"><h2>Generated files</h2><ul>''' + ''.join(file_links) + '''</ul></section>
</main>
<script>
const xyzData = ''' + json.dumps(xyz_data) + ''';
const homoCube = ''' + json.dumps(homo_data) + ''';
const lumoCube = ''' + json.dumps(lumo_data) + ''';
let viewer = null;
function initializeViewer() {
  if (!xyzData || typeof $3Dmol === 'undefined') return;
  viewer = $3Dmol.createViewer('viewer', {backgroundColor: 'white'});
  viewer.addModel(xyzData, 'xyz');
  viewer.setStyle({}, {stick: {radius: 0.17}, sphere: {scale: 0.28}});
  viewer.zoomTo();
  viewer.render();
  document.getElementById('homoButton').disabled = !homoCube;
  document.getElementById('lumoButton').disabled = !lumoCube;
}
function clearOrbitalSurfaces() {
  if (!viewer) return;
  if (typeof viewer.removeAllSurfaces === 'function') viewer.removeAllSurfaces();
  if (typeof viewer.removeAllShapes === 'function') viewer.removeAllShapes();
}
function showStructure() {
  if (!viewer) return;
  clearOrbitalSurfaces();
  viewer.render();
}
function showOrbital(kind) {
  if (!viewer) return;
  const cube = kind === 'homo' ? homoCube : lumoCube;
  if (!cube) return;
  clearOrbitalSurfaces();
  const volume = new $3Dmol.VolumeData(cube, 'cube');
  viewer.addIsosurface(volume, {isoval: 0.03, color: 'blue', opacity: 0.65, smoothness: 5});
  viewer.addIsosurface(volume, {isoval: -0.03, color: 'red', opacity: 0.65, smoothness: 5});
  viewer.render();
}
window.addEventListener('load', initializeViewer);
</script>
</body>
</html>'''
  with open(report_path, 'w', encoding='utf-8') as handle:
    handle.write(document)
  print('HTML report written:', report_path)
  return report_path


def _postprocess_orca_job(input_path, output_path):
  """Create frontier-orbital cubes and an HTML report for a completed ORCA job."""
  if not os.path.isfile(output_path) or os.path.getsize(output_path) == 0:
    return None
  base_prefix = os.path.splitext(output_path)[0]
  lower_name = os.path.basename(base_prefix).lower()
  if lower_name.endswith(('_cation', '_anion')) or lower_name in {'product', 'reactant', 'ts'}:
    return None

  details = {'Engine': 'ORCA', 'Input file': os.path.basename(input_path), 'Output file': os.path.basename(output_path)}
  details.update(_parse_orca_method_details(input_path))
  try:
    details['Final electronic energy (Eh)'] = format(_extract_final_scf_energy(output_path), '.12f')
  except Exception:
    pass

  homo_cube = None
  lumo_cube = None
  try:
    homo, lumo, gap_eh, gap_ev = _save_homo_lumo_results(output_path, base_prefix)
    details['HOMO orbital'] = homo['number']
    details['HOMO energy (eV)'] = format(homo['energy_ev'], '.6f')
    details['LUMO orbital'] = lumo['number']
    details['LUMO energy (eV)'] = format(lumo['energy_ev'], '.6f')
    details['HOMO-LUMO gap (eV)'] = format(gap_ev, '.6f')
    homo_cube = _generate_orca_mo_cube(base_prefix, homo['number'], 'HOMO')
    lumo_cube = _generate_orca_mo_cube(base_prefix, lumo['number'], 'LUMO')
  except Exception as orbital_error:
    print('ORCA frontier-orbital post-processing skipped:', orbital_error)

  xyz_path = _find_structure_file(base_prefix, input_path=input_path)
  data_files = [input_path, output_path, base_prefix + '.property.txt', homo_cube, lumo_cube]
  return _generate_html_report(
    base_prefix,
    'ORCA',
    details,
    xyz_path=xyz_path,
    homo_cube=homo_cube,
    lumo_cube=lumo_cube,
    data_files=data_files
  )




def _read_xyz_atoms(xyz_path):
  """Read a conventional XYZ file and return (symbol, x, y, z) records."""
  if not os.path.isfile(xyz_path):
    raise FileNotFoundError('XYZ file was not found: ' + xyz_path)
  with open(xyz_path, 'r', encoding='utf-8', errors='replace') as handle:
    lines = handle.readlines()
  if len(lines) < 3:
    raise ValueError('XYZ file does not contain an atom block: ' + xyz_path)
  atoms = []
  for line in lines[2:]:
    fields = line.split()
    if len(fields) < 4:
      continue
    try:
      atoms.append((fields[0], float(fields[1]), float(fields[2]), float(fields[3])))
    except ValueError:
      continue
  if not atoms:
    raise ValueError('No Cartesian atoms could be parsed from: ' + xyz_path)
  return atoms


def _write_xyz_atoms(atoms, xyz_path, comment='Generated by GUIDE'):
  """Write Cartesian atom records as an XYZ file."""
  with open(xyz_path, 'w', encoding='utf-8') as handle:
    handle.write(str(len(atoms)) + '\n')
    handle.write(str(comment) + '\n')
    for symbol, x_value, y_value, z_value in atoms:
      handle.write(
        '{0:3s} {1: .10f} {2: .10f} {3: .10f}\n'.format(
          str(symbol), float(x_value), float(y_value), float(z_value)
        )
      )
  return xyz_path


def _pdb_to_xyz(pdb_path, xyz_path):
  """Convert ATOM/HETATM coordinates from a MOPAC PDB file into XYZ."""
  atoms = []
  with open(pdb_path, 'r', encoding='utf-8', errors='replace') as handle:
    for line in handle:
      if not line.startswith(('ATOM  ', 'HETATM')):
        continue
      symbol = line[76:78].strip()
      if not symbol:
        atom_name = re.sub(r'[^A-Za-z]', '', line[12:16]).strip()
        symbol = atom_name[:2].capitalize() if len(atom_name) > 1 and atom_name[1].islower() else atom_name[:1].upper()
      try:
        x_value = float(line[30:38])
        y_value = float(line[38:46])
        z_value = float(line[46:54])
      except ValueError:
        fields = line.split()
        if len(fields) < 9:
          continue
        try:
          x_value, y_value, z_value = map(float, fields[6:9])
        except ValueError:
          continue
      atoms.append((symbol, x_value, y_value, z_value))
  if not atoms:
    raise ValueError('No atoms could be parsed from MOPAC PDB: ' + pdb_path)
  return _write_xyz_atoms(atoms, xyz_path, 'Optimized geometry generated by MOPAC')


def _mopac_coordinate_block(atoms, optimize=False):
  """Create MOPAC Cartesian coordinates with optimization flags."""
  flag = 1 if optimize else 0
  rows = []
  for symbol, x_value, y_value, z_value in atoms:
    rows.append(
      '{0:3s} {1: .10f} {2:d} {3: .10f} {4:d} {5: .10f} {6:d}'.format(
        str(symbol), float(x_value), flag,
        float(y_value), flag, float(z_value), flag
      )
    )
  return '\n'.join(rows)


def _write_mopac_cartesian_input(input_path, keywords, atoms, optimize=False, title='GUIDE MOPAC calculation'):
  """Write a complete MOPAC data set in Cartesian form."""
  with open(input_path, 'w', encoding='utf-8') as handle:
    handle.write(str(keywords).strip() + '\n')
    handle.write(str(title).strip() + '\n')
    handle.write('Generated automatically by the GUIDE YASARA plugin\n')
    handle.write(_mopac_coordinate_block(atoms, optimize=optimize))
    handle.write('\n\n')
  return input_path


def _mopac_output_has_results(output_path):
  """Check that MOPAC produced usable output without a clear fatal marker."""
  if not os.path.isfile(output_path) or os.path.getsize(output_path) == 0:
    return False

  content = _read_text(output_path).upper()
  fatal_markers = (
    'ERROR:  ',
    'FATAL ERROR',
    'CALCULATION ABANDONED',
    'JOB STOPPED BY OPERATOR',
    'UNRECOGNIZED KEY-WORD',
    'UNRECOGNIZED KEYWORD',
    'SCF FAILED TO CONVERGE',
    'TOO MANY ITERATIONS'
  )
  if any(marker in content for marker in fatal_markers):
    return False

  result_markers = (
    '== MOPAC DONE ==',
    'FINAL HEAT OF FORMATION',
    'HEAT OF FORMATION',
    'TOTAL ENERGY',
    'HOMO LUMO ENERGIES',
    'CI TRANS.'
  )
  return any(marker in content for marker in result_markers)


def _mopac_terminated_normally(output_path):
  """Return True when MOPAC printed its normal completion marker."""
  if not os.path.isfile(output_path) or os.path.getsize(output_path) == 0:
    return False
  content = _read_text(output_path).upper()
  return '== MOPAC DONE ==' in content


def _parse_mopac_single_point_energies(output_path):
  """Parse the final energy summary from a MOPAC output file."""
  if not os.path.isfile(output_path):
    return {}

  patterns = {
    'heat_of_formation_kcal_mol': re.compile(
      r'(?:FINAL\s+)?HEAT\s+OF\s+FORMATION\s*=\s*'
      r'([-+]?\d*\.?\d+(?:[EeDd][-+]?\d+)?)\s*KCAL(?:/MOL)?',
      re.IGNORECASE
    ),
    'heat_of_formation_kj_mol': re.compile(
      r'(?:FINAL\s+)?HEAT\s+OF\s+FORMATION.*?=\s*'
      r'[-+]?\d*\.?\d+(?:[EeDd][-+]?\d+)?\s*KCAL(?:/MOL)?\s*=\s*'
      r'([-+]?\d*\.?\d+(?:[EeDd][-+]?\d+)?)\s*KJ(?:/MOL)?',
      re.IGNORECASE
    ),
    'total_energy_ev': re.compile(
      r'TOTAL\s+ENERGY\s*=\s*'
      r'([-+]?\d*\.?\d+(?:[EeDd][-+]?\d+)?)\s*EV',
      re.IGNORECASE
    ),
    'electronic_energy_ev': re.compile(
      r'ELECTRONIC\s+ENERGY\s*=\s*'
      r'([-+]?\d*\.?\d+(?:[EeDd][-+]?\d+)?)\s*EV',
      re.IGNORECASE
    ),
    'core_core_repulsion_ev': re.compile(
      r'CORE-CORE\s+REPULSION\s*=\s*'
      r'([-+]?\d*\.?\d+(?:[EeDd][-+]?\d+)?)\s*EV',
      re.IGNORECASE
    )
  }

  values = {}
  with open(output_path, 'r', encoding='utf-8', errors='replace') as handle:
    for line in handle:
      for key, pattern in patterns.items():
        match = pattern.search(line)
        if match:
          try:
            values[key] = float(
              match.group(1).replace('D', 'E').replace('d', 'e')
            )
          except ValueError:
            pass

  return values


def _format_mopac_single_point_message(energies, output_path):
  """Create a readable YASARA message for a MOPAC single-point job."""
  message_lines = ['MOPAC single-point calculation completed successfully.']

  if 'total_energy_ev' in energies:
    message_lines.append(
      'Total energy: ' + format(energies['total_energy_ev'], '.8f') + ' eV'
    )
  if 'electronic_energy_ev' in energies:
    message_lines.append(
      'Electronic energy: ' +
      format(energies['electronic_energy_ev'], '.8f') + ' eV'
    )
  if 'core_core_repulsion_ev' in energies:
    message_lines.append(
      'Core-core repulsion: ' +
      format(energies['core_core_repulsion_ev'], '.8f') + ' eV'
    )
  if 'heat_of_formation_kcal_mol' in energies:
    message_lines.append(
      'Heat of formation: ' +
      format(energies['heat_of_formation_kcal_mol'], '.6f') + ' kcal/mol'
    )
  if 'heat_of_formation_kj_mol' in energies:
    message_lines.append(
      'Heat of formation: ' +
      format(energies['heat_of_formation_kj_mol'], '.6f') + ' kJ/mol'
    )

  message_lines.append('Output file: ' + str(output_path))
  return '\n'.join(message_lines)


def _extract_mopac_scalar(output_path, label):
  """Return the final numeric value printed on a labelled MOPAC output line."""
  pattern = re.compile(
    re.escape(label) + r'\s*=\s*([-+]?\d*\.?\d+(?:[EeDd][-+]?\d+)?)',
    re.IGNORECASE
  )
  value = None
  with open(output_path, 'r', encoding='utf-8', errors='replace') as handle:
    for line in handle:
      match = pattern.search(line)
      if match:
        value = float(match.group(1).replace('D', 'E').replace('d', 'e'))
  return value


def _parse_mopac_homo_lumo(output_path):
  """Parse the final MOPAC HOMO/LUMO energies when present."""
  pattern = re.compile(
    r'HOMO\s+LUMO\s+ENERGIES\s*\(EV\)\s*=\s*'
    r'([-+]?\d*\.?\d+(?:[EeDd][-+]?\d+)?)\s+'
    r'([-+]?\d*\.?\d+(?:[EeDd][-+]?\d+)?)',
    re.IGNORECASE
  )
  result = None
  with open(output_path, 'r', encoding='utf-8', errors='replace') as handle:
    for line in handle:
      match = pattern.search(line)
      if match:
        homo_value = float(match.group(1).replace('D', 'E').replace('d', 'e'))
        lumo_value = float(match.group(2).replace('D', 'E').replace('d', 'e'))
        result = (homo_value, lumo_value, lumo_value - homo_value)
  return result


def _parse_mopac_uv_transitions(output_path):
  """Parse MOPAC's CI transition-energy/wavelength/oscillator-strength table."""
  with open(output_path, 'r', encoding='utf-8', errors='replace') as handle:
    lines = handle.readlines()

  header_indices = [
    index for index, line in enumerate(lines)
    if 'WAVELENGTH' in line.upper() and 'OSCILLATOR' in line.upper()
  ]
  if not header_indices:
    raise ValueError(
      'MOPAC did not print a CI wavelength/oscillator-strength table. '
      'Inspect the output and verify that INDO or MECI/C.I. completed.'
    )

  transitions = []
  data_started = False
  non_data_count = 0
  numeric_pattern = re.compile(r'^[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][-+]?\d+)?$')
  for line in lines[header_indices[-1] + 1:]:
    fields = line.replace(',', ' ').split()
    if not fields:
      if data_started:
        non_data_count += 1
        if non_data_count >= 3:
          break
      continue
    try:
      state = int(fields[0])
    except ValueError:
      if data_started:
        non_data_count += 1
        if non_data_count >= 5:
          break
      continue

    numeric_values = []
    for token in fields[1:]:
      cleaned = token.strip().replace('D', 'E').replace('d', 'e')
      if numeric_pattern.fullmatch(cleaned):
        try:
          numeric_values.append(float(cleaned))
        except ValueError:
          continue
    if len(numeric_values) < 4:
      continue

    energy_ev, frequency_cm, wavelength_nm, oscillator_strength = numeric_values[:4]
    if energy_ev <= 0 or wavelength_nm <= 0 or not np.isfinite(wavelength_nm):
      continue
    transitions.append({
      'state': state,
      'energy_ev': energy_ev,
      'frequency_cm-1': frequency_cm,
      'wavelength_nm': wavelength_nm,
      'oscillator_strength': max(0.0, oscillator_strength)
    })
    data_started = True
    non_data_count = 0

  if not transitions:
    raise ValueError('No positive-energy MOPAC electronic transitions could be parsed.')
  unique = {}
  for transition in transitions:
    unique[(transition['state'], round(transition['energy_ev'], 8))] = transition
  return sorted(unique.values(), key=lambda item: item['energy_ev'])


def _write_mopac_uv_csv(path, transitions):
  """Write parsed MOPAC vertical excitations to CSV."""
  with open(path, 'w', encoding='utf-8', newline='') as handle:
    writer = csv.writer(handle)
    writer.writerow([
      'State', 'Excitation_energy_eV', 'Frequency_cm-1',
      'Wavelength_nm', 'Oscillator_strength'
    ])
    for transition in transitions:
      writer.writerow([
        transition['state'], transition['energy_ev'],
        transition['frequency_cm-1'], transition['wavelength_nm'],
        transition['oscillator_strength']
      ])
  return path


def _create_mopac_uv_plot(
  transitions,
  image_path,
  minimum_wavelength=150.0,
  maximum_wavelength=800.0,
  fwhm_nm=15.0
):
  """Create stick and Gaussian-broadened MOPAC UV-Visible spectra."""
  minimum_wavelength = float(minimum_wavelength)
  maximum_wavelength = float(maximum_wavelength)
  if maximum_wavelength <= minimum_wavelength:
    raise ValueError('Maximum UV wavelength must exceed the minimum wavelength.')
  sigma = max(float(fwhm_nm), 0.01) / 2.354820045
  grid = np.linspace(minimum_wavelength, maximum_wavelength, 4000)
  spectrum = np.zeros_like(grid)
  visible_transitions = []
  for transition in transitions:
    wavelength = float(transition['wavelength_nm'])
    strength = float(transition['oscillator_strength'])
    if wavelength < minimum_wavelength or wavelength > maximum_wavelength:
      continue
    visible_transitions.append(transition)
    spectrum += strength * np.exp(-0.5 * ((grid - wavelength) / sigma) ** 2)
  if not visible_transitions:
    raise ValueError('No MOPAC transitions fall within the requested wavelength range.')
  if float(np.max(spectrum)) > 0:
    spectrum = spectrum / float(np.max(spectrum))

  figure = plt.figure(figsize=(10, 6))
  axis = figure.add_subplot(111)
  axis.plot(grid, spectrum, linewidth=1.8, label='Gaussian-broadened spectrum')
  maximum_strength = max(
    max(float(item['oscillator_strength']) for item in visible_transitions),
    1.0e-12
  )
  for transition in visible_transitions:
    normalized_strength = float(transition['oscillator_strength']) / maximum_strength
    axis.vlines(
      float(transition['wavelength_nm']), 0.0, normalized_strength,
      linewidth=0.8, alpha=0.65
    )
  axis.set_xlim(minimum_wavelength, maximum_wavelength)
  axis.set_ylim(bottom=0.0)
  axis.set_xlabel('Wavelength (nm)')
  axis.set_ylabel('Normalized intensity')
  axis.set_title('MOPAC UV-Visible spectrum')
  axis.legend()
  axis.grid(alpha=0.2)
  figure.tight_layout()
  figure.savefig(image_path, dpi=180)
  plt.close(figure)
  return image_path


def _postprocess_mopac_job(input_path):
  """Create a generic HTML result report for a completed MOPAC calculation."""
  input_path = os.path.abspath(input_path)
  base_prefix = os.path.splitext(input_path)[0]
  output_path = base_prefix + '.out'
  if not os.path.isfile(output_path) or os.path.getsize(output_path) == 0:
    return None

  details = {
    'Engine': 'MOPAC',
    'Input file': os.path.basename(input_path),
    'Output file': os.path.basename(output_path)
  }
  energy_values = _parse_mopac_single_point_energies(output_path)
  if 'heat_of_formation_kcal_mol' in energy_values:
    details['Heat of formation (kcal/mol)'] = format(
      energy_values['heat_of_formation_kcal_mol'], '.8f'
    )
  if 'heat_of_formation_kj_mol' in energy_values:
    details['Heat of formation (kJ/mol)'] = format(
      energy_values['heat_of_formation_kj_mol'], '.8f'
    )
  if 'total_energy_ev' in energy_values:
    details['Total energy (eV)'] = format(
      energy_values['total_energy_ev'], '.8f'
    )
  if 'electronic_energy_ev' in energy_values:
    details['Electronic energy (eV)'] = format(
      energy_values['electronic_energy_ev'], '.8f'
    )
  if 'core_core_repulsion_ev' in energy_values:
    details['Core-core repulsion (eV)'] = format(
      energy_values['core_core_repulsion_ev'], '.8f'
    )
  homo_lumo = _parse_mopac_homo_lumo(output_path)
  if homo_lumo is not None:
    details['HOMO energy (eV)'] = format(homo_lumo[0], '.6f')
    details['LUMO energy (eV)'] = format(homo_lumo[1], '.6f')
    details['HOMO-LUMO gap (eV)'] = format(homo_lumo[2], '.6f')

  xyz_path = base_prefix + '_optimized.xyz'
  pdb_path = base_prefix + '.pdb'
  if os.path.isfile(pdb_path):
    try:
      _pdb_to_xyz(pdb_path, xyz_path)
    except Exception as conversion_error:
      print('MOPAC PDB-to-XYZ conversion skipped:', conversion_error)
  if not os.path.isfile(xyz_path):
    original_xyz = base_prefix + '.xyz'
    xyz_path = original_xyz if os.path.isfile(original_xyz) else None

  return _generate_html_report(
    base_prefix,
    'MOPAC',
    details,
    xyz_path=xyz_path,
    data_files=[
      input_path, output_path, base_prefix + '.arc',
      pdb_path, base_prefix + '.aux', xyz_path
    ]
  )


def _run_mopac_uv_pipeline(
  project_prefix,
  source_xyz,
  theory,
  charge,
  multiplicity,
  excitation_model,
  active_orbitals,
  minimum_wavelength,
  maximum_wavelength,
  fwhm_nm
):
  """Optimize with a PMx method, then calculate and plot vertical excitations."""
  if str(multiplicity).upper() != 'SINGLET':
    raise ValueError(
      'The automated MOPAC UV-Visible workflow currently supports closed-shell '
      'singlets only because INDO/S and the CI spectrum are run with RHF.'
    )
  active_orbitals = int(active_orbitals)
  if active_orbitals < 2:
    raise ValueError('The MOPAC C.I. active space must contain at least two orbitals.')
  if active_orbitals % 2 != 0:
    active_orbitals += 1

  initial_atoms = _read_xyz_atoms(source_xyz)
  optimization_base = project_prefix + '_mopac_uv_opt'
  optimization_input = optimization_base + '.mop'
  optimization_output = optimization_base + '.out'
  optimization_keywords = (
    str(theory) + ' RHF CHARGE=' + str(int(float(charge))) +
    ' SINGLET PRECISE GNORM=0.5 XYZ PDBOUT AUX'
  )
  _write_mopac_cartesian_input(
    optimization_input,
    optimization_keywords,
    initial_atoms,
    optimize=True,
    title='GUIDE MOPAC ground-state geometry optimization for UV-Visible analysis'
  )
  yasara.ShowMessage('MOPAC ground-state geometry optimization is in progress.')
  optimization_return_code = _run_mopac(optimization_input)
  if optimization_return_code != 0 or not _mopac_output_has_results(optimization_output):
    raise RuntimeError('MOPAC ground-state optimization failed. Inspect ' + optimization_output)

  optimized_xyz = optimization_base + '_optimized.xyz'
  optimization_pdb = optimization_base + '.pdb'
  if os.path.isfile(optimization_pdb):
    _pdb_to_xyz(optimization_pdb, optimized_xyz)
  else:
    # PDBOUT may not be available in older builds; retain the input geometry
    # rather than silently terminating the entire spectroscopy workflow.
    _write_xyz_atoms(
      initial_atoms,
      optimized_xyz,
      'Input geometry used because MOPAC did not create a PDB file'
    )
  optimized_atoms = _read_xyz_atoms(optimized_xyz)

  spectrum_base = project_prefix + '_mopac_uv'
  spectrum_input = spectrum_base + '.mop'
  spectrum_output = spectrum_base + '.out'
  if str(excitation_model).upper().startswith('INDO'):
    spectrum_method = 'INDO/S (ZINDO/S)'
    spectrum_keywords = (
      'INDO CIS C.I.=' + str(active_orbitals) +
      ' MECI 1SCF RHF CHARGE=' + str(int(float(charge))) + ' SINGLET'
    )
  else:
    spectrum_method = str(theory) + ' MECI/CIS'
    spectrum_keywords = (
      str(theory) + ' CIS C.I.=' + str(active_orbitals) +
      ' MECI 1SCF RHF CHARGE=' + str(int(float(charge))) + ' SINGLET'
    )
  _write_mopac_cartesian_input(
    spectrum_input,
    spectrum_keywords,
    optimized_atoms,
    optimize=False,
    title='GUIDE MOPAC vertical electronic-excitation calculation'
  )
  yasara.ShowMessage('MOPAC vertical excitation and oscillator-strength calculation is in progress.')
  spectrum_return_code = _run_mopac(spectrum_input)
  if spectrum_return_code != 0 or not os.path.isfile(spectrum_output):
    raise RuntimeError('MOPAC UV-Visible calculation failed. Inspect ' + spectrum_output)

  transitions = _parse_mopac_uv_transitions(spectrum_output)
  transition_csv = spectrum_base + '_transitions.csv'
  spectrum_png = spectrum_base + '_spectrum.png'
  _write_mopac_uv_csv(transition_csv, transitions)
  _create_mopac_uv_plot(
    transitions,
    spectrum_png,
    minimum_wavelength=minimum_wavelength,
    maximum_wavelength=maximum_wavelength,
    fwhm_nm=fwhm_nm
  )

  details = {
    'Engine': 'MOPAC',
    'Calculation': 'Ground-state optimization followed by vertical UV-Visible excitations',
    'Geometry method': str(theory),
    'Excited-state model': spectrum_method,
    'C.I. active orbitals': active_orbitals,
    'Charge': int(float(charge)),
    'Multiplicity': multiplicity,
    'Spectrum range (nm)': str(minimum_wavelength) + ' - ' + str(maximum_wavelength),
    'Gaussian FWHM (nm)': fwhm_nm,
    'Number of parsed transitions': len(transitions)
  }
  heat = _extract_mopac_scalar(optimization_output, 'FINAL HEAT OF FORMATION')
  if heat is not None:
    details['Optimized heat of formation (kcal/mol)'] = format(heat, '.8f')

  report_path = _generate_html_report(
    spectrum_base,
    'MOPAC',
    details,
    xyz_path=optimized_xyz,
    image_paths=[spectrum_png],
    data_files=[
      optimization_input, optimization_output, optimization_base + '.arc',
      optimization_pdb, optimized_xyz,
      spectrum_input, spectrum_output, spectrum_base + '.arc',
      transition_csv, spectrum_png
    ]
  )
  return {
    'report': report_path,
    'image': spectrum_png,
    'csv': transition_csv,
    'optimized_xyz': optimized_xyz,
    'transitions': transitions
  }


print(sys.executable)

macrotarget_input = str(yasara.selection[0].text[0]).strip().strip('\"')
nameobj = str(yasara.selection[0].text[1]).strip()
nameobj = str(nameobj) + '_obj1'
print(nameobj)

if macrotarget_input == '':
  yasara.ShowMessage("GUIDE must need a directory")
  yasara.plugin.end()
else:
  macrotarget = os.path.abspath(os.path.expanduser(macrotarget_input))
  os.makedirs(macrotarget, exist_ok=True)
  write_test_path = os.path.join(macrotarget, '.guide_write_test')
  try:
    with open(write_test_path, 'w', encoding='utf-8') as write_test:
      write_test.write('ok')
  finally:
    _safe_remove(write_test_path)
  print('ok')
mod=(platform.system())
if mod== 'Linux' or mod == 'Darwin':
  mod=str(1)
  print('Linux')
else:
  mod=str(2)
  print('Windows')
yasarapath=os.getcwd()
if os.path.isfile(yasarapath+'/'+'module.txt'):
  print('++++')
else:
  modulelist =\
    yasara.ShowWin("Custom","modules",400,250,
     "Text", 20, 50, "Do you want to install essential modules?",
     "RadioButtons",2,1,
                    20, 100,"yes",
                    200,100,"no",
     "Button",      150,200," O K")
  attach= open((yasarapath)+'/'+'module.txt','w+')
  attach.write((str(modulelist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
  attach.close()  
  f = open((yasarapath)+'/'+'module.txt', "r")
  content= f.readlines()
  f.close()
  a = str((content[0]).strip('\n'))   
  
  if a == str(1):
    print(sys.executable)
    pypath= sys.executable
    modulepath= open(yasarapath+'/'+'module.txt','w')
    modulepath.write(str(pypath).replace('python.exe','').replace('pythonw.exe',''))
    modulepath.close()
    rmodule=open(yasarapath+'/'+'module.txt')
    pmodule= rmodule.readlines()
    rmodule.close()
    moduleroad= str((pmodule[0]).strip('\n'))
    print(moduleroad)
    if mod == str(2):
      os.chdir(moduleroad)    
      md= open(moduleroad+'/'+'module_command.txt','w+')
      md.write("Step1: Check the Python version used by YASARA:\n'python --version'\n\nStep2: Install pip:\n'curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py'\n'python get-pip.py'\n\nStep3: Install the modules used inside YASARA:\n'python -m pip install --upgrade pip'\n'python -m pip install rdkit pandas numpy matplotlib'\n\nThe csv, json, shutil, subprocess and html modules are included with Python and must not be installed separately.")
      md.close()   

      md_macro= open(macrotarget+'/'+'module_command.txt','w+')
      md_macro.write("Step1: Check the Python version used by YASARA:\n'python --version'\n\nStep2: Install pip:\n'curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py'\n'python get-pip.py'\n\nStep3: Install the modules used inside YASARA:\n'python -m pip install --upgrade pip'\n'python -m pip install rdkit pandas numpy matplotlib'\n\nThe csv, json, shutil, subprocess and html modules are included with Python and must not be installed separately.")
      md_macro.close()  

      yasara.ShowMessage("Please go to "+str(moduleroad)+" and follow the steps as given in module_command.txt")
      yasara.run("wait continuebutton")

    else:
      md_macro= open(macrotarget+'/'+'module_command.txt','w+')
      md_macro.write("Step1: Check the Python version used by YASARA:\n'python --version'\n\nStep2: Install pip:\n'curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py'\n'python get-pip.py'\n\nStep3: Install the modules used inside YASARA:\n'python -m pip install --upgrade pip'\n'python -m pip install rdkit pandas numpy matplotlib'\n\nThe csv, json, shutil, subprocess and html modules are included with Python and must not be installed separately.")
      md_macro.close()  

      yasara.ShowMessage("Please go to "+str(macrotarget)+" and follow the steps as given in module_command.txt")
      yasara.run("wait continuebutton") 
    #for python 3.8  
    #_run_legacy_command('curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py')
    #_run_legacy_command('python get-pip.py')
    #_run_legacy_command('pip install pandas')
    #_run_legacy_command('pip install numpy')   
    #_run_legacy_command('pip install matplotlib')    
    #_run_legacy_command('pip install python-csv')    
    #_run_legacy_command('pip install pytest-shutil')
    
    #for 3.10 or later version
    #_run_legacy_command('python -m pip install pip==22.2.2')
    #_run_legacy_command('py -m pip install pandas')
    #_run_legacy_command('py -m pip install numpy')   
    #_run_legacy_command('py -m pip install matplotlib')    
    #_run_legacy_command('py -m pip install python-csv')    
    #_run_legacy_command('py -m pip install pytest-shutil') 
  else:
    print('++')  
  

import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv
from rdkit import Chem




#storing the path and method information in variables

methods= str((yasara.selection[0].list))
method= (methods.strip('[]'))
method= (method.replace("'", "").replace(",",""))

print(method)
 
plgpath=yasarapath
#sentence= macrotarget
#a=(sentence.count('/'))
#print(a)
#a= str(a)


print(mod)  

print(plgpath)

## storing ORCA/MOPAC paths

if method == 'ORCA':
  orca_path_file = os.path.join(plgpath, 'orcapath.txt')

  if os.path.isfile(orca_path_file):
    print('orca...')
    orcap = _read_path_file(orca_path_file)
  else:
    pathlist = yasara.ShowWin(
      "Custom", "ORCA-PATH", 400, 250,
      "TextInput", 20, 48, "Please insert the ORCA folder path", 150, 150,
      "Button", 150, 200, " O K"
    )
    orcap = _dialog_value(pathlist)
    with open(orca_path_file, 'w', encoding='utf-8') as path_handle:
      path_handle.write(orcap)

  if os.path.isfile(orcap):
    orca = os.path.abspath(orcap)
    orcap = os.path.dirname(orca)
  else:
    orca_name = 'orca.exe' if mod == str(2) else 'orca'
    orca = os.path.join(orcap, orca_name)

  print(orca)
  if not os.path.isfile(orca):
    yasara.ShowMessage('ORCA executable was not found:\n' + orca)
    yasara.plugin.end()

elif method == 'MOPAC':
  mopac_path_file = os.path.join(plgpath, 'mopacpath.txt')

  if os.path.isfile(mopac_path_file):
    mopac_folder = _read_path_file(mopac_path_file)
  else:
    pathlist = yasara.ShowWin(
      "Custom", "MOPAC-PATH", 400, 250,
      "TextInput", 20, 48, "Please insert the MOPAC folder path", 150, 150,
      "Button", 150, 200, " O K"
    )
    mopac_folder = _dialog_value(pathlist)
    with open(mopac_path_file, 'w', encoding='utf-8') as path_handle:
      path_handle.write(mopac_folder)

  if os.path.isfile(mopac_folder):
    mopac = os.path.abspath(mopac_folder)
  else:
    mopac_candidates = [
      os.path.join(mopac_folder, 'mopac.exe'),
      os.path.join(mopac_folder, 'MOPAC.exe'),
      os.path.join(mopac_folder, 'MOPAC2016.exe'),
      os.path.join(mopac_folder, 'mopac')
    ]
    mopac = next(
      (candidate for candidate in mopac_candidates if os.path.isfile(candidate)),
      mopac_candidates[0]
    )

  if not os.path.isfile(mopac):
    yasara.ShowMessage('MOPAC executable was not found:\n' + mopac)
    yasara.plugin.end()

else:
  yasara.ShowMessage("GUIDE must need a QM method")
  yasara.plugin.end()
####OPTIONS FOR ORCA  
if method == 'ORCA':
  yasara.ShowMessage('Make sure that ORCA is installed and path is provided in ..yasara/plg/orcapath.txt')
  #yasara.run("LabelAll 'Make sure that ORCA is installed and path is provided in orcapath.txt',Height=0.9,Color=Black,X=0,Y=19,Z=65")
  calculationlist=\
    yasara.ShowWin("Custom","CALCULATION",600,400,
    "Text", 20, 48, "Calculation type",
    "RadioButtons",11,1,
                   20, 65,"Single point",
                   20, 105,"Geometry optimization",
                   20, 155,"Transition state",
                   20, 205,"Vibrational frequencies",
                   20, 255,"UV-Vis spectroscopy",
                   20, 300,"HOMO-LUMO energy gap",
                   200, 65,"None of these",
                   20, 350,"Constraining QM",
                   200,155,"Multilevel DFT",
                   250,205,"Fukui function",
                   250,255,"NMR spectroscopy",
    "Button",      542,348," O K")    


  cal=open(macrotarget+'/'+'calculation.txt','w+')
  cal.write((str(calculationlist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
  cal.close()
  methos_cal = open(macrotarget+'/'+'calculation.txt', "r")
  caltype= methos_cal.readlines()
  methos_cal.close()

  if os.path.getsize(macrotarget+'/'+'calculation.txt') == 0:
    yasara.ShowMessage("QM calculation failed, select a specific method") 
    _safe_remove(macrotarget+'/'+'calculation.txt')
    yasara.plugin.end() 
  else:
    print('ok') 

  methodology= str((caltype[0]).strip('\n')) 
  print(methodology)
  yasara.run('Wait ContinueButton')
  #yasara.run("LabelAll 'Make sure that ORCA is installed and path is provided in orcapath.txt',Height=0.9,Color=Black,X=0,Y=19,Z=65")
  #yasara.run('UnlabelAll')
####MOPAC options
elif method == 'MOPAC':
  yasara.ShowMessage('Make sure that MOPAC is installed and path is provided in ..yasara/plg/mopacpath.txt')
  calculationlist=\
    yasara.ShowWin("Custom","CALCULATION",600,400,
    "Text", 20, 48, "Theory",
    "RadioButtons",7,1,
                   20, 65,"AM1",
                   20, 105,"PM3",
                   20, 145,"PM6",
                   20, 185,"PM7",
                   160, 65,"RM1",
                   160, 105,"MNDO",
                   160, 145,"MNDOD",
    "Text", 20, 239, "HF type:",
    "RadioButtons",2,1,
                   20, 265,"RHF",
                   120, 265,"UHF",
    "List",        350,70,"Calculation type",220,175,"No",                 
                   5,    "Single-point",
                          "HOMO-LUMO",
                          "Equilibrium-geometry",
                          "UV-Vis spectroscopy",
                          "Import-job",
    "Button",      542,348," O K")   

  # Preserve the raw ShowWin result for troubleshooting without destroying
  # spaces in option names such as "UV-Vis spectroscopy".
  with open(macrotarget+'/'+'calculation.txt', 'w', encoding='utf-8') as cal:
    cal.write(repr(calculationlist))

  theory_index, hf_index, methodology = _parse_mopac_dialog_result(
    calculationlist
  )

  if theory_index is None or hf_index is None:
    yasara.ShowMessage(
      "Could not read the selected MOPAC theory and HF type. "
      "Please restart the calculation."
    )
    yasara.plugin.end()

  if not methodology:
    yasara.ShowMessage(
      "Could not determine the selected MOPAC calculation type. "
      "Raw dialog result was saved in calculation.txt."
    )
    yasara.plugin.end()

  theory = str(theory_index)
  hf = str(hf_index)
  print('MOPAC dialog:', calculationlist)
  print('MOPAC calculation:', methodology)

  ## HF
  if hf == str(1):
    hf = "RHF"
  elif hf == str(2):
    hf = "UHF"
  else:
    yasara.ShowMessage(
      "Could not determine the selected MOPAC HF type."
    )
    yasara.plugin.end()

  print(hf)

  ## Theory
  mopac_theory_map = {
    '1': 'AM1',
    '2': 'PM3',
    '3': 'PM6',
    '4': 'PM7',
    '5': 'RM1',
    '6': 'MNDO',
    '7': 'MNDOD'
  }

  if theory not in mopac_theory_map:
    yasara.ShowMessage(
      "Could not determine the selected MOPAC theory."
    )
    yasara.plugin.end()

  theory = mopac_theory_map[theory]
  print(theory)

  # Initialize the keyword variables before any downstream branch can use
  # them. Each calculation type then receives its own explicit keyword set.
  firstkey = ''
  secondkey = ''
  thirdkey = ''

  mopac_keyword_sets = {
    'Single-point': (
      'AUX 1SCF LARGE CHARGE=',
      'NOOPT',
      'PDBOUT THREADS=1'
    ),
    'HOMO-LUMO': (
      '1SCF GRAPH VECTORS ALLVEC BONDS CHARGE=',
      'EIGS',
      'PDBOUT THREADS=1'
    ),
    'Equilibrium-geometry': (
      'AUX LARGE CHARGE=',
      'BONDS XYZ PRNT=2 PRTXYZ FLEPO PRECISE GNORM=0.0',
      'PDBOUT THREADS=1'
    )
  }

  if methodology in mopac_keyword_sets:
    firstkey, secondkey, thirdkey = mopac_keyword_sets[methodology]

  elif methodology == 'UV-Vis spectroscopy':
    # A dedicated two-stage ground-state optimization + vertical-excitation
    # workflow is executed in the MOPAC calculation section below.
    pass

  elif methodology == 'Import-job':
    nonelist =\
      yasara.ShowWin("Custom","PROVIDE YOUR OWN FILE",400,250,
      "TextInput", 20, 48,"Insert the name of the file with extension(.mop)",150,150,
      "Button",      150,200," O K")
    nonek=open(macrotarget+'/'+'file.txt','w+')
    nonek.write((str(nonelist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
    nonek.close()
    none_fk = open(macrotarget+'/'+'file.txt', "r")
    ownfileinfo = [
      line.strip()
      for line in none_fk.readlines()
      if line.strip()
    ]
    none_fk.close()

    if not ownfileinfo:
      yasara.ShowMessage(
        "No MOPAC input filename was provided."
      )
      yasara.plugin.end()

    ownfile = str(ownfileinfo[0]).strip()
 


#### ORCA INPUT FILE FORMATION 
if method == 'ORCA' and methodology == str(7):
  trjlist =\
    yasara.ShowWin("Custom","Create own QM project",400,250,
     "Text", 20, 50, "Do you want default functional,basis set?",
     "RadioButtons",2,1,
                    20, 100,"yes",
                    200,100,"no",
     "Button",      150,200," O K")
  attach= open((macrotarget)+'/'+'ownfileorca.txt','w+')
  attach.write((str(trjlist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
  attach.close()  
  f = open((macrotarget)+'/'+'ownfileorca.txt', "r")
  content= f.readlines()
  f.close()
  uqm = str((content[0]).strip('\n'))  
  if uqm == str(2):
    keylist =\
      yasara.ShowWin("Custom","ORCA-kEYWORDS",400,250,
      "TextInput", 20, 48,"Please insert the functional keyword",150,150,   
      "TextInput", 20, 110,"Please insert the basis keyword",150,150,
      "Button",      150,200," O K")
    key=open(macrotarget+'/'+'keyword.txt','w+')
    key.write((str(keylist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
    key.close()
    if os.path.getsize(macrotarget+'/'+'keyword.txt') == 0:
      yasara.ShowMessage("QM calculation failed, please insert a correct functional and basis set information. Restart the process") 
      _safe_remove(macrotarget+'/'+'keyword.txt')
      yasara.plugin.end() 
    else:
      print('ok')   
    fkey = open(macrotarget+'/'+'keyword.txt', "r")
    keyword= fkey.readlines()
    fkey.close()
    functional= str((keyword[0]).strip('\n'))
    basis=' '.join(keyword[1:]))#str((keyword[1]).strip('\n'))
    print(functional)
    print(basis)     



###################################################################################################
###all the below section will come under transition state for orca  
if method == 'ORCA' and methodology == str(3) :
  ##Building a reactant molecule by user
  yasara.ShowMessage("Please build your reactant molecule and then click continue")
  yasara.run("wait continuebutton")
  yasara.run("BFactorAtom all,0")
  #yasara.run('ForceField AMBER03,SetPar=Yes')
###charge of the reactant molecule
  #chargeinfo=yasara.run('ChargeObj all')
  yasara.run('JoinObj all,1')
  yasara.run('SaveSMILES 1 ,'+macrotarget+'/'+str(nameobj)+'.smiles,transform=Yes')
  yasara.ShowMessage("Charge calculation is in process...")
  time.sleep(5)  
  smi=open(macrotarget+"/"+str(nameobj)+".smiles",'r')
  smidata=smi.read()
  smi.close()
  mol=_require_molecule_from_smiles(smidata)
  chargeinfo=Chem.GetFormalCharge(mol)
  cfmod=open(macrotarget+'/'+str(nameobj)+'charge.log','w')
  cfmod.write(str(chargeinfo).replace('Summed up net charge is ','').replace('[','').replace(']','').replace(',','\n'))
  cfmod.close()
  if os.path.getsize(macrotarget+'/'+str(nameobj)+'charge.log') == 0:
    yasara.ShowMessage("Charge calculation failed, restart the process") 
    _safe_remove(macrotarget+'/'+str(nameobj)+'charge.log')
    yasara.plugin.end() 
  else:
    print('ok')   

  chargef= open(macrotarget+'/'+str(nameobj)+'charge.log','r')
  chargeall=chargef.readlines()
  chargef.close()
  charge=float((chargeall[0]).strip('\n'))
  charge=round(charge)
  print(charge)
  alllist =\
    yasara.ShowWin("Custom","INFORMATION",400,250,
    "NumberInput", 20, 88,"Charge",str(charge),-1000,1000,
    "NumberInput", 180, 88,"Multiplicity",1,1,1000,
    "Button",      150,200," O K")  
##counting the object present in the yasara window
  rcharge=open(macrotarget+'/'+str(nameobj)+'charge.log','w+')
  rcharge.write((str(alllist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
  rcharge.close()
  if os.path.getsize(macrotarget+'/'+str(nameobj)+'charge.log') == 0:
    yasara.ShowMessage("Charge calculation failed, restart the process") 
    _safe_remove(macrotarget+'/'+str(nameobj)+'charge.log')
    yasara.plugin.end() 
  else:
    print('ok')   

  react_charge = open(macrotarget+'/'+str(nameobj)+'charge.log', "r")
  reactinfo= react_charge.readlines()
  react_charge.close()
  reactcharge= str((reactinfo[0]).strip('\n'))    
  reactmultiplicity= str((reactinfo[1]).strip('\n')) 

  obj=yasara.run("CountObj all")
  deltext= open(macrotarget+'/'+'deltext.txt','w')
  deltext.write(str(obj).replace('object(s) match the selection.','').replace('[','').replace(']',''))
  deltext.close()
  g = open((macrotarget)+'/'+'deltext.txt', "r")
  content = g.readlines()
  noobj=str((content[0]).strip('\n'))
  g.close()
  _safe_remove((macrotarget)+'/'+'deltext.txt')
  if noobj == str(0):
    yasara.ShowMessage("Please build at least one molecule or see the terminal")
    print("C'mon, we can not calculate TS for a blank space !!!")
    yasara.plugin.end()
  
  else:
    yasara.run('JoinObj all,1')
    noatom=yasara.run("CountAtom all")
    atomtext= open(macrotarget+'/'+'atomnotext.txt','w')
    atomtext.write(str(noatom).replace('atom(s) match the selection.','').replace('[','').replace(']',''))
    atomtext.close()
    a = open((macrotarget)+'/'+'atomnotext.txt', 'r')
    atomcontent = a.readlines()
    atom=str((atomcontent[0]).strip('\n'))
    atom=int(atom)
    a.close()
    _safe_remove((macrotarget)+'/'+'atomnotext.txt')
    i=0
    for i in range (0,atom):
      
        yasara.run("BFactorAtom "+str(i+1)+","+str(i+1))
        bfactor=yasara.run("BFactorAtom "+str(i+1))
        if i == 0:
          val= open(macrotarget+'/'+'bfactor.txt','w')
          val.write(str(bfactor).replace('[','').replace(']','').replace('.0',''))
          val.close()
        else:
          valread=open(macrotarget+'/'+'bfactor.txt','r')
          value=valread.readlines()
          valread.close()
          rewrite=open(macrotarget+'/'+'bfactor.txt','w')
          rewrite.writelines(value)
          rewrite.write('\n')
          rewrite.write(str(bfactor).replace('[','').replace(']',''))
          rewrite.close()
        
        i=i+1
##Saving the xyz file of the reactant
  yasara.run("SaveXYZ 1,"+str(macrotarget)+'/'+"reactant.xyz,transform=Yes") 
  time.sleep(5)
##modifying the reactant.xyz file without hamparing the main file
  with open(str(macrotarget)+'/'+'reactant.xyz', 'r') as fin:
      data = fin.read().splitlines(True)
  with open(str(macrotarget)+'/'+'reactant.txt', 'w') as fout:
      fout.writelines(data[2:]) 
      fout.close()
   
##concatination of reactant xyz info with its b-factor value   
  combine =[]

  with open((macrotarget)+'/'+'bfactor.txt') as xh:
    with open((macrotarget)+'/'+'reactant.txt') as yh:
      with open((macrotarget)+'/'+'reactant_filter.txt',"w") as zh:
         #Read first file
         xlines = xh.readlines()
         #Read second file
         ylines = yh.readlines()
         #Combine content of both lists
         #combine = list(zip(ylines,xlines))
         #Write to third file
         for i in range(len(xlines)):
            line = ylines[i].strip('\n') + '    ' + xlines[i]
            zh.write(line)
#_safe_remove((macrotarget)+'/'+'reactant.txt')
   
   

if method == 'ORCA' and (methodology in {str(1), str(2), str(3), str(4), str(5), str(6), str(8), str(10), str(11)} or (methodology == str(7) and uqm == str(1))):
  resultlist =\
    yasara.ShowWin("Custom","Functional and Basis set",600,400,
    "Text", 20, 48, "Functional set:",
    "RadioButtons",14,1,
                   20, 65,"B3LYP",
                   20, 105,"BLYP",
                   20, 155,"HF",
                   20, 205,"MP2",
                   20, 255,"CCSD",
                   20, 305,"PBE",
                   140, 65,"revPBE",
                   140, 105,"PBE0",
                   140, 155,"B97-3C",
                   140, 205,"M06L Grid6",
                   140, 255,"XTB",
                   140, 305,"wB97X-D3",
                   20, 350,"None",
                   140, 350,"PM3",
    "List",        360,70,"Basis set",190,128,"No",                 
                   20,    "DEF2-SVP",
                          "DEF2-TZVP",
                          "DEF2-QZVP",
                          "DEF2-TZVPP",
                          "DEF2-QZVPP",
                          "DEF2-TZVPPD",
                          "ma-def2-SVP",
                          "ma-def2-TZVP",
                          "6-31G(d)",
                          "cc-pVDZ",
                          "cc-pVTZ",
                          "cc-pVQZ",
                          "aug-cc-pVDZ",
                          "aug-cc-pVTZ",
                          "aug-cc-pVQZ",
                          "pcSseg-1",
                          "pcSseg-2",
                          "pcJ-1",
                          "pcJ-2",
                          "none",
    "Button",      542,348," O K")

  pathYasara = os.getcwd()
  temp= open((pathYasara)+'/'+'ytempo.ini', 'w+')
  temp.write((str(resultlist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
  temp.write('\n')
  temp.close()
  ycalcline= open((pathYasara)+'/'+'ytempo.ini')
  for line in ycalcline:
      if "0" in line:
         yasara.ShowMessage("GUIDE must need a specific functional and basis set information for ORCA")
         yasara.plugin.end()
      else:
         print('ok')
  ycalcline.close()


#the tempo.ini contains the input file information
  if os.path.getsize((pathYasara)+'/'+'ytempo.ini') == 1:
    yasara.ShowMessage("QM calculation failed, please insert a correct functional and basis set information. Restart the process") 
    _safe_remove((pathYasara)+'/'+'ytempo.ini')
    yasara.plugin.end() 
  else:
    print('ok')  
  f = open(pathYasara+'/'+'ytempo.ini', "r")
  content= f.readlines()
  f.close()
  functional= str((content[0]).strip('\n'))
  nothing=str((content[1]).strip('\n'))
  basis=str((content[2]).strip('\n'))      
  #yasara.run('UnlabelAll')
    
     
  if functional == str(1):
    functional="B3LYP"
  elif functional == str(2):
    functional="BLYP"
  elif functional == str(3):
    functional="HF"
  elif functional == str(4):
    functional="MP2"
  elif functional == str(5):
    functional="CCSD"
  elif functional == str(6):
    functional="PBE"
  elif functional == str(7):
    functional="revPBE"
  elif functional == str(8):
    functional="PBE0"
  elif functional == str(9):
    functional="B97-3C"
  elif functional == str(10):
    functional="M06L Grid6"
  elif functional == str(11):
    functional="XTB"
    basis= ''
  elif functional == str(14):
    functional="RHF PM3"
    basis= ''
  elif functional == str(13):
    keylist =\
      yasara.ShowWin("Custom","ORCA-kEYWORDS",400,250,
      "TextInput", 20, 48,"Please insert the functional keyword",150,150,   
      "TextInput", 20, 110,"Please insert the basis keyword",150,150,
      "Button",      150,200," O K")
    key=open(macrotarget+'/'+'keyword.txt','w+')
    key.write((str(keylist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
    key.close()
    if os.path.getsize(macrotarget+'/'+'keyword.txt') == 0:
      yasara.ShowMessage("QM calculation failed, please insert a correct functional and basis set information. Restart the process") 
      _safe_remove(macrotarget+'/'+'keyword.txt')
      yasara.plugin.end() 
    else:
      print('ok')   
    fkey = open(macrotarget+'/'+'keyword.txt', "r")
    keyword= fkey.readlines()
    fkey.close()
    functional= str((keyword[0]).strip('\n'))
    basis=  ' '.join(keyword[1:])#str((keyword[1]).strip('\n'))
    print(functional)
    print(basis)   
  
  else:
    functional="wB97X-D3"

  print(functional)
  print(basis)

else:
  print('qui')
#####QM/QM2###functional and basis set for qm atoms
if method == 'ORCA' and methodology == str(9) :
  resultlist =\
    yasara.ShowWin("Custom","QM atoms",600,400,
    "Text", 20, 48, "Functional set:",
    "RadioButtons",14,1,
                   20, 65,"B3LYP",
                   20, 105,"BLYP",
                   20, 155,"HF",
                   20, 205,"MP2",
                   20, 255,"CCSD",
                   20, 305,"PBE",
                   140, 65,"revPBE",
                   140, 105,"PBE0",
                   140, 155,"B97-3C",
                   140, 205,"M06L Grid6",
                   140, 255,"XTB",
                   140, 305,"wB97X-D3",
                   20, 350,"None",
                   140, 350,"PM3",
    "List",        360,70,"Basis set",190,128,"No",                 
                   20,    "DEF2-SVP",
                          "DEF2-TZVP",
                          "DEF2-QZVP",
                          "DEF2-TZVPP",
                          "DEF2-QZVPP",
                          "DEF2-TZVPPD",
                          "ma-def2-SVP",
                          "ma-def2-TZVP",
                          "6-31G(d)",
                          "cc-pVDZ",
                          "cc-pVTZ",
                          "cc-pVQZ",
                          "aug-cc-pVDZ",
                          "aug-cc-pVTZ",
                          "aug-cc-pVQZ",
                          "pcSseg-1",
                          "pcSseg-2",
                          "pcJ-1",
                          "pcJ-2",
                          "none",
    "Button",      542,348," O K")

  pathYasara = os.getcwd()
  temp= open((pathYasara)+'/'+'ytempo.ini', 'w+')
  temp.write((str(resultlist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
  temp.write('\n')
  temp.close()

  ycalcline= open((pathYasara)+'/'+'ytempo.ini')
  for line in ycalcline:
      if "0" in line:
         yasara.ShowMessage("GUIDE must need a specific functional and basis set information for ORCA")
         yasara.plugin.end()
      else :
         print('ok')
  ycalcline.close()
#the tempo.ini contains the input file information
  if os.path.getsize((pathYasara)+'/'+'ytempo.ini') == 1:
    yasara.ShowMessage("QM calculation failed, please insert a correct functional and basis set information. Restart the process") 
    _safe_remove((pathYasara)+'/'+'ytempo.ini')
    yasara.plugin.end() 
  else:
    print('ok')  

  f = open(pathYasara+'/'+'ytempo.ini', "r")
  content= f.readlines()
  f.close()
  functional= str((content[0]).strip('\n'))
  nothing=str((content[1]).strip('\n'))
  basis=str((content[2]).strip('\n'))      

    
     
  if functional == str(1):
    functional="B3LYP"
  elif functional == str(2):
    functional="BLYP"
  elif functional == str(3):
    functional="HF"
  elif functional == str(4):
    functional="MP2"
  elif functional == str(5):
    functional="CCSD"
  elif functional == str(6):
    functional="PBE"
  elif functional == str(7):
    functional="revPBE"
  elif functional == str(8):
    functional="PBE0"
  elif functional == str(9):
    functional="B97-3C"
  elif functional == str(10):
    functional="M06L Grid6"
  elif functional == str(11):
    functional="XTB"
    basis= ''
  elif functional == str(14):
    functional="RHF PM3"
    basis= ''
  elif functional == str(13):
    keylist =\
      yasara.ShowWin("Custom","ORCA-kEYWORDS",400,250,
      "TextInput", 20, 48,"Please insert the functional keyword",150,150,   
      "TextInput", 20, 110,"Please insert the basis keyword",150,150,
      "Button",      150,200," O K")
    key=open(macrotarget+'/'+'keyword.txt','w+')
    key.write((str(keylist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
    key.close()
    if os.path.getsize(macrotarget+'/'+'keyword.txt') == 0:
      yasara.ShowMessage("QM calculation failed, please insert a correct functional and basis set information. Restart the process") 
      _safe_remove(macrotarget+'/'+'keyword.txt')
      yasara.plugin.end() 
    else:
      print('ok')  

    fkey = open(macrotarget+'/'+'keyword.txt', "r")
    keyword= fkey.readlines()
    fkey.close()
    functional= str((keyword[0]).strip('\n'))
    basis=str((keyword[1]).strip('\n'))
    print(functional)
    print(basis)   
  
  else:
    functional="wB97X-D3"

  print(functional)
  print(basis)
###functional and basis set for other atoms 
  qm2resultlist =\
    yasara.ShowWin("Custom","QM2 atoms",600,400,
    "Text", 20, 48, "Functional set:",
    "RadioButtons",14,1,
                   20, 65,"B3LYP",
                   20, 105,"BLYP",
                   20, 155,"HF",
                   20, 205,"MP2",
                   20, 255,"CCSD",
                   20, 305,"PBE",
                   140, 65,"revPBE",
                   140, 105,"PBE0",
                   140, 155,"B97-3C",
                   140, 205,"M06L Grid6",
                   140, 255,"XTB",
                   140, 305,"wB97X-D3",
                   20, 350,"None",
                   140, 350,"PM3",
    "List",        360,70,"Basis set",190,128,"No",                 
                   20,    "DEF2-SVP",
                          "DEF2-TZVP",
                          "DEF2-QZVP",
                          "DEF2-TZVPP",
                          "DEF2-QZVPP",
                          "DEF2-TZVPPD",
                          "ma-def2-SVP",
                          "ma-def2-TZVP",
                          "6-31G(d)",
                          "cc-pVDZ",
                          "cc-pVTZ",
                          "cc-pVQZ",
                          "aug-cc-pVDZ",
                          "aug-cc-pVTZ",
                          "aug-cc-pVQZ",
                          "pcSseg-1",
                          "pcSseg-2",
                          "pcJ-1",
                          "pcJ-2",
                          "none",
    "Button",      542,348," O K")

  pathYasara = os.getcwd()
  tempqm2= open((pathYasara)+'/'+'tempo_qm2.ini', 'w+')
  tempqm2.write((str(qm2resultlist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
  tempqm2.write('\n')
  tempqm2.close()
  ycalcline= open((pathYasara)+'/'+'tempo_qm2.ini')
  for line in ycalcline:
      if "0" in line:
         yasara.ShowMessage("GUIDE must need a specific functional and basis set information for ORCA")
         yasara.plugin.end()
      else:
         print('ok')
  ycalcline.close()

  if os.path.getsize((pathYasara)+'/'+'tempo_qm2.ini') == 1:
    yasara.ShowMessage("QM calculation failed, please insert a correct functional and basis set information. Restart the process") 
    _safe_remove((pathYasara)+'/'+'tempo_qm2.ini')
    yasara.plugin.end() 
  else:
    print('ok')  

#the tempo.ini contains the input file information
  fqm2 = open(pathYasara+'/'+'tempo_qm2.ini', "r")
  contentqm2= fqm2.readlines()
  fqm2.close()
  functionalqm2= str((contentqm2[0]).strip('\n'))
  nothingqm2=str((contentqm2[1]).strip('\n'))
  basisqm2=str((contentqm2[2]).strip('\n'))      

    
     
  if functionalqm2 == str(1):
    functionalqm2="B3LYP"
  elif functionalqm2 == str(2):
    functionalqm2="BLYP"
  elif functionalqm2 == str(3):
    functionalqm2="HF"
  elif functionalqm2 == str(4):
    functionalqm2="MP2"
  elif functionalqm2 == str(5):
    functionalqm2="CCSD"
  elif functionalqm2 == str(6):
    functionalqm2="PBE"
  elif functionalqm2 == str(7):
    functionalqm2="revPBE"
  elif functionalqm2 == str(8):
    functionalqm2="PBE0"
  elif functionalqm2 == str(9):
    functionalqm2="B97-3C"
  elif functionalqm2 == str(10):
    functionalqm2="M06L Grid6"
  elif functionalqm2 == str(11):
    functionalqm2="XTB"
    basisqm2= ''
  elif functionalqm2 == str(14):
    functionalqm2="RHF PM3"
    basisqm2= ''
  elif functionalqm2 == str(13):
    qmkeylist =\
      yasara.ShowWin("Custom","ORCA-kEYWORDS",400,250,
      "TextInput", 20, 48,"Please insert the functional keyword",150,150,   
      "TextInput", 20, 110,"Please insert the basis keyword",150,150,
      "Button",      150,200," O K")
    keyqm2=open(macrotarget+'/'+'keywordqm2.txt','w+')
    keyqm2.write((str(qmkeylist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
    keyqm2.close()
    if os.path.getsize(macrotarget+'/'+'keywordqm2.txt') == 0:
      yasara.ShowMessage("QM calculation failed, please insert a correct functional and basis set information. Restart the process") 
      _safe_remove(macrotarget+'/'+'keywordqm2.txt')
      yasara.plugin.end() 
    else:
      print('ok')  

    qm2fkey = open(macrotarget+'/'+'keywordqm2.txt', "r")
    qm2keyword= qm2fkey.readlines()
    qm2fkey.close()
    functionalqm2= str((qm2keyword[0]).strip('\n'))
    basisqm2=str((qm2keyword[1]).strip('\n'))
    print(functionalqm2)
    print(basisqm2)   
  
  else:
    functionalqm2="wB97X-D3"

  print(functionalqm2)
  print(basisqm2)  
##################for transition state calculation
if method == 'ORCA' and methodology in {str(3), str(8), str(9)}:  
  #orca='/home/picasso/Documents/orca/orca_4_1_2_linux_x86-64_openmpi313/orca'
  if methodology == str(3):
    imgalllist =\
        yasara.ShowWin("Custom","No of points",400,250,
        "Text",        50, 50,"*Select the  total number of reaction point",
        "NumberInput", 20, 85,"points",8,8,100,
        "Button",      150,200," O K")  
##counting the object present in the yasara window
    rimg=open(macrotarget+'/'+str(nameobj)+'images.log','w+')
    rimg.write((str(imgalllist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
    rimg.close()
    if os.path.getsize(macrotarget+'/'+str(nameobj)+'images.log') == 0:
      yasara.ShowMessage("QM calculation failed. Must need the number of reaction points. Please restart the process") 
      _safe_remove(macrotarget+'/'+str(nameobj)+'procharge.log')
      yasara.plugin.end() 

    img = open(macrotarget+'/'+str(nameobj)+'images.log', "r")
    noimg= img.readlines()
    img.close()
    numeroimg= str((noimg[0]).strip('\n'))    


  if methodology == str(3):
    orcareactinp=open((macrotarget)+'/'+'reactant.txt')
    reactdata=orcareactinp.read()
    orcareactinp.close()
    orca_geo_react=open((macrotarget)+'/'+'reactant.inp','w+')
    orca_geo_react.write("!")
    orca_geo_react.write(str(functional))
    orca_geo_react.write(" ")
    orca_geo_react.write(str(basis))
    orca_geo_react.write(" ")
    orca_geo_react.write("OPT")
    #orca_geo_react.write("\n%pal\n   nprocs ")
    #orca_geo_react.write(str(processor))
    #orca_geo_react.write('\nend')
    orca_geo_react.write("\n\n*xyz ")
    orca_geo_react.write(str(reactcharge))
    orca_geo_react.write(" ")
    orca_geo_react.write(str(reactmultiplicity))
    orca_geo_react.write("\n")
    orca_geo_react.write(str(reactdata))
    orca_geo_react.write("\n")
    orca_geo_react.write("*")
    orca_geo_react.close()
    yasara.ShowMessage("orca is optimizing the geometry of reactant")
  #_safe_move(macrotarget+'/'+'reactant.xyz', macrotarget+'/'+'prev_reactant.xyz')
    if mod == str(1) or mod == str(2):
      _run_legacy_command(str(orca)+' '+macrotarget+'/'+'reactant.inp > '+macrotarget+'/'+'reactant.out') 
    else:
      _run_legacy_command('orca '+macrotarget+'/'+'reactant.inp > '+macrotarget+'/'+'reactant.out')  


###############################################################################
    _safe_remove((macrotarget)+'/'+'bfactor.txt')
    yasara.run("Clear")
    yasara.run('Loadxyz '+macrotarget+'/'+'reactant.xyz')
    #yasara.run("DuplicateAll")
    #yasara.run("DelObj 1")
    yasara.run('BFactorAtom all,0')
    cnoatom=yasara.run("CountAtom all")
    catomtext= open(macrotarget+'/'+'catomnotext.txt','w')
    catomtext.write(str(cnoatom).replace('atom(s) match the selection.','').replace('[','').replace(']',''))
    catomtext.close()
    ca = open((macrotarget)+'/'+'catomnotext.txt', 'r')
    catomcontent = ca.readlines()
    catom=str((catomcontent[0]).strip('\n'))
    catom=int(catom)
    ca.close()
    _safe_remove((macrotarget)+'/'+'catomnotext.txt')
    ci=0
    for ci in range (0,catom):
      
        yasara.run("BFactorAtom "+str(ci+1)+","+str((ci+1)))
        
    ci=ci+1
    yasara.run("LabelAll 'Do not update hydrogen after bond modification',Height=1.9,Color=Yellow,X=0,Y=19,Z=65")
    yasara.ShowMessage("Please modify the reactant to build product molecule and then click continue")
    yasara.run("wait continuebutton")
    #yasara.ExperimentMinimization()
    #yasara.Experiment("On")
    #yasara.Wait("ExpEnd")
    #yasara.run('DelObj simcell')
    yasara.run('InflateObj all')
    yasara.run('DeflateAll')
    yasara.run('InflateAll')

##Calculating the charge of the product
    #prochargeinfo=yasara.run('ChargeObj all')
    yasara.run('JoinObj all,1')
    yasara.run('SaveSMILES 1 ,'+macrotarget+'/'+str(nameobj)+'.smiles,transform=Yes')
    yasara.ShowMessage("Charge calculation is in process...")
    time.sleep(5)    
    smi=open(macrotarget+'/'+str(nameobj)+".smiles","r")
    smidata=smi.read()
    smi.close()
    mol=_require_molecule_from_smiles(smidata)
    prochargeinfo=Chem.GetFormalCharge(mol)
    promod=open(macrotarget+'/'+str(nameobj)+'procharge.log','w')
    promod.write(str(prochargeinfo).replace('Summed up net charge is ','').replace('[','').replace(']',''))
    promod.close()
    prochargef= open(macrotarget+'/'+str(nameobj)+'procharge.log','r')
    prochargeall=prochargef.readlines()
    prochargef.close()
    procharge=float((prochargeall[0]).strip('\n'))
    procharge=round(procharge)
    print(procharge)

    proalllist =\
      yasara.ShowWin("Custom","INFORMATION",400,250,
      "NumberInput", 20, 88,"Charge",str(procharge),-1000,1000,
      "NumberInput", 180, 88,"Multiplicity",1,1,1000,
      "Button",      150,200," O K")  
##counting the object present in the yasara window
    pcharge=open(macrotarget+'/'+str(nameobj)+'procharge.log','w+')
    pcharge.write((str(proalllist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
    pcharge.close()

    if os.path.getsize(macrotarget+'/'+str(nameobj)+'procharge.log') == 0:
      yasara.ShowMessage("Charge calculation failed, restart the process") 
      _safe_remove(macrotarget+'/'+str(nameobj)+'procharge.log')
      yasara.plugin.end() 
    else:
      print('ok')   
    pro_charge = open(macrotarget+'/'+str(nameobj)+'procharge.log', "r")
    productinfo= pro_charge.readlines()
    pro_charge.close()
    productcharge= str((productinfo[0]).strip('\n'))    
    productmultiplicity= str((productinfo[1]).strip('\n')) 


  ##counting the atom of product present in the yasara window
    proatom=yasara.run("Countatom all")
    prodeltext= open(macrotarget+'/'+'prodeltext.txt','w')
    prodeltext.write(str(proatom).replace('atom(s) match the selection.','').replace('[','').replace(']',''))
    prodeltext.close()
    p = open((macrotarget)+'/'+'prodeltext.txt', "r")
    pcontent = p.readlines()
    nopro=str((pcontent[0]).strip('\n').strip('[').strip(']'))
    p.close()
    atom=str(atom)
    _safe_remove((macrotarget)+'/'+'prodeltext.txt')
##checking the number of atom in product and reactant are same or not

    if nopro == atom :
    #yasara.run('JoinObj all,1')
      j=0
      nopro=int(nopro)
      for j in range (0,nopro):
          bfactor=yasara.run("BFactorAtom "+str(j+1))
          if j == 0:
            val= open(macrotarget+'/'+'product_bfactor.txt','w')
            val.write(str(bfactor).replace('[','').replace(']','').replace('.0',''))
            val.close()
          else:
            valread=open(macrotarget+'/'+'product_bfactor.txt','r')
            value=valread.readlines()
            valread.close()
            rewrite=open(macrotarget+'/'+'product_bfactor.txt','w')
            rewrite.writelines(value)
            rewrite.write('\n')
            rewrite.write(str(bfactor).replace('[','').replace(']','').replace('.0',''))
            rewrite.close()
        
          j=j+1 
    else:
     yasara.ShowMessage("WARNING! please see the terminal")
     print(nopro)
     print(atom)
     print("No. of atoms must be same for reactant and product")
     yasara.plugin.end()        


##Saving the xyz file of the product
    yasara.run("SaveXYZ all,"+str(macrotarget)+'/'+"product.xyz,transform=Yes") 
##modifying the reactant.xyz file without hamparing the main file
    time.sleep(5)
    with open(str(macrotarget)+'/'+'product.xyz', 'r') as fin:
        data = fin.read().splitlines(True)
    with open(str(macrotarget)+'/'+'product.txt', 'w') as fout:
        fout.writelines(data[2:]) 
        fout.close()
   
##concatination of reactant xyz info with its b-factor value   
    procombine =[]

    with open((macrotarget)+'/'+'product.txt') as xh:
      with open((macrotarget)+'/'+'product_bfactor.txt') as yh:
        with open((macrotarget)+'/'+'product_filter.txt',"w") as zh:
       #Read first file
           xlines = xh.readlines()
         #Read second file
           ylines = yh.readlines()
         #Combine content of both lists
         #combine = list(zip(ylines,xlines))
         #Write to third file
           for i in range(len(xlines)):
              line = ylines[i].strip('\n') + '    ' + xlines[i]
              zh.write(line)
    _safe_remove((macrotarget)+'/'+'product.txt')
    _safe_remove((macrotarget)+'/'+'product_bfactor.txt')
    _safe_remove((macrotarget)+'/'+'reactant_filter.txt')
    yasara.run("clear")
    yasara.run("DelObj all")
    yasara.run('Loadxyz '+macrotarget+'/'+'reactant.xyz')
    yasara.run('Loadxyz '+macrotarget+'/'+'product.xyz')
    radius=yasara.run('RadiusObj 1')
    rd=open(macrotarget+'/'+'radius.txt','w+')
    rd.write(str(radius).replace('[','').replace(']','').replace('Object  1 (reactant) has a VdW radius of ','').replace('A from its geometric center',''))
    rd.close()
    fk=open(macrotarget+'/'+'radius.txt','r')
    r=fk.readline()
    fk.close()
    r=str(r)
    r=float(r)
    display_offset = 15
    y = r + display_offset
    y=str(y)
    z = -r - display_offset
    z=str(z)
#yasara.run('r=RadiusObj 1')
#yasara.run('len=15')
    yasara.run('MoveObj !1,X='+str(y))
    yasara.run('MoveObj 1,X='+str(z))
    yasara.run('ShowArrow Start=Point,X=-15,Y=0,Z=50,End=Point,X=15,Y=0,Z=50,Radius=1,Color=Yellow')
    yasara.run('ZoomAll Steps=0')
    yasara.run('Move Z=20')
    yasara.run('LabelObj 1,reactant,Color=Yellow,Y=5,Z=-5')
    yasara.run('LabelObj 2,product,Color=Yellow,Y=5,Z=-5')

    def sortLinesByColumn(readable, column, columnt_type):
        """Returns a list of strings (lines in readable file) in sorted order (based on column)"""
        lines = []

        for line in readable:
          # get the element in column based on which the lines are to be sorted
            column_element= columnt_type(line.split(' ')[column-1])
            lines.append((column_element, line))

        lines.sort()

        return [x[1] for x in lines]


    with open((macrotarget)+'/'+'product_filter.txt') as f:
      # sort the lines based on column 1, and column 1 is type int
        sorted_lines = sortLinesByColumn(f, 1, int)
        k= open((macrotarget)+'/'+'product_final.txt',"w")
        k.writelines(sorted_lines)
        k.close()

    _safe_remove((macrotarget)+'/'+'product_filter.txt')
    proedit = open((macrotarget)+'/'+'product_final.txt', "r")
    editfile = open((macrotarget)+'/'+'product_filter.txt', "w")
    for line in proedit:
        if line.strip():
            editfile.write("\t".join(line.split()[1:]) + "\n")    
    proedit.close()
    editfile.close()
    _safe_remove((macrotarget)+'/'+'product_final.txt')
#######################################################
    orcaproinp=open((macrotarget)+'/'+'product_filter.txt')
    prodata=orcaproinp.read()
    orcaproinp.close()
    print(prodata)
    orca_geo_pro=open((macrotarget)+'/'+'product.inp','w+')
    orca_geo_pro.write("!")
    orca_geo_pro.write(str(functional))
    orca_geo_pro.write(" ")
    orca_geo_pro.write(str(basis))
    orca_geo_pro.write(" ")
    orca_geo_pro.write("OPT")
    #orca_geo_pro.write("\n%pal\n   nprocs ")
    #orca_geo_pro.write(str(processor))
    #orca_geo_pro.write('\nend')
    orca_geo_pro.write("\n\n*xyz ")
    orca_geo_pro.write(str(productcharge))
    orca_geo_pro.write(" ")
    orca_geo_pro.write(str(productmultiplicity))
    orca_geo_pro.write("\n")
  #orca_geo_pro.write(str(reactdata))
    orca_geo_pro.write(str(prodata))
    orca_geo_pro.write("\n")
    orca_geo_pro.write("*")
    orca_geo_pro.close()

    yasara.ShowMessage("orca is optimizing the geometry of product")
    if mod == str(1) or mod == str(2):
      _run_legacy_command(str(orca)+' '+macrotarget+'/'+'product.inp > '+macrotarget+'/'+'product.out')
    else:
      _run_legacy_command('orca '+macrotarget+'/'+'product.inp > '+macrotarget+'/'+'product.out')
  
    yasara.ShowMessage("Geometry optimization is complete")
    tsinp=open((macrotarget)+'/'+'ts.inp','w+')
    tsinp.write('!')
    tsinp.write(str(functional))
    tsinp.write(' ')
    tsinp.write(str(basis))
    tsinp.write(' NEB-TS FREQ ')
    #tsinp.write("\n%pal\n   nprocs ")
    #tsinp.write(str(processor))
    #tsinp.write('\nend')    
    tsinp.write('\n%geom ReducePrint false end\n%neb\n\nNEB_End_XYZFile "product.xyz"\n\nNImages ')
    tsinp.write(str(numeroimg))
    tsinp.write('\n\nend\n\n*xyzfile ')
    tsinp.write(str(reactcharge))
    tsinp.write(' ')
    tsinp.write(str(reactmultiplicity))
    tsinp.write(' reactant.xyz\n\n')
    tsinp.close()
    yasara.ShowMessage("Transition state calculation is in process..")
    os.chdir(pathYasara)
    os.chdir(macrotarget)
    time.sleep(5)
    if mod == str(1) or mod == str(2): 
      _run_legacy_command(orca+' ts.inp >ts.out')
    else:
      _run_legacy_command('orca ts.inp >ts.out')

    if os.path.isfile(macrotarget+'/'+'ts_MEP_trj.xyz') :
      trjlist =\
        yasara.ShowWin("Custom","Trjectory view",400,250,
         "Text", 20, 50, "Do you want to visualize trajectory?",
         "RadioButtons",2,1,
                        20, 100,"yes",
                        200,100,"no",
         "Button",      150,200," O K")
      attach= open((macrotarget)+'/'+'trjectory.txt','w+')
      attach.write((str(trjlist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
      attach.close()  
      f = open((macrotarget)+'/'+'trjectory.txt', "r")
      content= f.readlines()
      f.close()
      a = str((content[0]).strip('\n'))   
      if a == str(1):
        if mod == str(1):
          _safe_move(macrotarget+'/'+'ts_MEP_trj.xyz', macrotarget+'/'+'ts_MEP_final.xyz' )
        else:
           _safe_move(macrotarget+'/'+'ts_MEP_trj.xyz', macrotarget+'/'+'ts_MEP_final.xyz' )     
    
        yasara.run('DelObj all')  
        yasara.run('Loadxyz '+macrotarget+'/'+'ts_MEP_final.xyz')
        yasara.run('BallStickObj all')
        obj=yasara.run("CountObj all")
        deltext= open(macrotarget+'/'+'deltext.txt','w')
        deltext.write(str(obj).replace('object(s) match the selection.','').replace('[','').replace(']',''))
        deltext.close()
        g = open((macrotarget)+'/'+'deltext.txt', "r")
        content = g.readlines()
        noobj=str((content[0]).strip('\n'))
        g.close()
        noobj=int(noobj)
        k=0
        yasara.run('ZoomAll Steps=20')
        yasara.run('HideObj all')
        for k in range(0,noobj):
            yasara.run('ShowObj '+str(k+1))
            yasara.run('BallStickObj all')
            yasara.run("wait continuebutton")
            if int(k+1) == noobj :
              print('done')
            else:
              yasara.run('DelObj '+str(k+1))
            k=k+1
        yasara.ShowMessage("Transition state calculation is complete and results are saved in: "+ macrotarget)
  
    else:
      yasara.ShowMessage("Transition state calculation is complete and results are saved in: "+ macrotarget)    



#######QM-QM2 region########################################################## 
  elif methodology == str(9):
    #processorllist =\
        #yasara.ShowWin("Custom","No of Processor",400,250,
        #"NumberInput", 20, 88,"Processor",8,8,16,
        #"Button",      150,200," O K")  
##counting the object present in the yasara window
   # numeroprocessor=open(macrotarget+'/'+'processor.log','w+')
    #numeroprocessor.write((str(processorllist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
    #numeroprocessor.close()
    #process = open(macrotarget+'/'+'processor.log', "r")
    #processornumber= process.readlines()
    #processor= str((processornumber[0]).strip('\n'))    
   
    yasara.ShowMessage("Please load Your structure")
    print(functional)
    print(basis)
    print(functionalqm2)
    print(basisqm2)
    if functionalqm2 == "RHF PM3":
      functionalqm2= "PM3"
    else:
      print(functional)
      print(functionalqm2)     
    
    print(functional)
    print(basis)
    print(functionalqm2)
    print(basisqm2)
    yasara.run("wait continuebutton")
    yasara.run("JoinObj all,1")
    
    yasara.run("SavePDB 1,"+str(macrotarget)+"/"+"MM.pdb")
    yasara.ShowMessage("Please select QM object(s) and then click continue")
    yasara.run("wait continuebutton")
    #yasara.run("JoinRes Selected")
    ####have to check
    yasara.run("NameAtom Selected, L")
    #yasara.run("NameAtom all and not selected, con")
    yasara.ShowMessage("Please additionally select QM2 atoms")
    yasara.run("wait continuebutton")
    #yasara.run("UnselectAll")
    #yasara.run("SelectAtom all with distance < 1 from L")
    ####have to check
    yasara.ShowMessage("Calculation is in progress...")
    yasara.run("DelAtom all !selected")
    yasara.run("UnselectAll")
    yasara.run("SelectAtom all and not L")
    yasara.run("NameRes selected,con")
    #yasara.run("NameAtom selected, con")
    #yasara.run("AddHydRes con")
    print('check###')
    yasara.run('BFactorAtom all,0')
    #yasara.run("wait continuebutton")
    countobj=yasara.run('CountObj all')

    #yasara.run("wait continuebutton")
    #yasara.run('joinObj all,1')    
    yasara.run("SavePDB all,"+str(macrotarget)+'/'+"QM.pdb,transform=Yes") 
    #yasara.run("SaveXYZ 1,"+str(macrotarget)+'/'+"QM.xyz,transform=Yes") 
    yasara.run('BFactorAtom all,0')
    cnoatom=yasara.run("CountAtom all")
    catomtext= open(macrotarget+'/'+'catomnotext.txt','w')
    catomtext.write(str(cnoatom).replace('atom(s) match the selection.','').replace('[','').replace(']',''))
    catomtext.close()
    ca = open((macrotarget)+'/'+'catomnotext.txt', 'r')
    catomcontent = ca.readlines()
    catom=str((catomcontent[0]).strip('\n'))
    catom=int(catom)
    ca.close()
    _safe_remove((macrotarget)+'/'+'catomnotext.txt')
    ci=0
    for ci in range (0,catom):
      
        yasara.run("BFactorAtom "+str(ci+1)+","+str((ci+1)-1))
        
    ci=ci+1
    yasara.run("DelAtom all and not L")

     
    bfactor=yasara.run("BFactorAtom all")
    
    yasara.ShowMessage("Charge calculation is in progress..")
    resnoatom=yasara.run("CountAtom all")
    resatomtext= open(macrotarget+'/'+'resatomnotext.txt','w')
    resatomtext.write(str(resnoatom).replace('atom(s) match the selection.','').replace('[','').replace(']',''))
    resatomtext.close()
    resa = open((macrotarget)+'/'+'resatomnotext.txt', 'r')
    resatomcontent = resa.readlines()
    resatom=str((resatomcontent[0]).strip('\n'))
    resatom=int(resatom)
    resa.close()
    _safe_remove((macrotarget)+'/'+'resatomnotext.txt')
    resi=0
    for i in range (0,resatom):
      
        #yasara.run("BFactorAtom "+str(resi+1)+","+str(resi+1))
        resbfactor=yasara.run("BFactorAtom "+str(resi+1))
        if i == 0:
          val= open(macrotarget+'/'+'check.inp','w')
          #val.write("{C ")
          val.write(str(resbfactor).replace('[','').replace(']','').replace('.0',''))
          #val.write(" C}")
          val.close()
        else:
          valread=open(macrotarget+'/'+'check.inp','r')
          value=valread.readlines()
          valread.close()
          rewrite=open(macrotarget+'/'+'check.inp','w')
          rewrite.writelines(value)
          rewrite.write(' ')
          #rewrite.write('{C ')
          rewrite.write(str(resbfactor).replace('[','').replace(']','').replace('.0',''))
          #rewrite.write(' C}')
          rewrite.close()
        
        resi=resi+1
    yasara.run("DelObj all")

    yasara.run('LoadPDB '+macrotarget+'/'+'QM.pdb')
    yasara.run('BFactorAtom all,0')
    noatom=yasara.run("CountAtom all")
    atomtext= open(macrotarget+'/'+'atomnotext.txt','w')
    atomtext.write(str(noatom).replace('atom(s) match the selection.','').replace('[','').replace(']',''))
    atomtext.close()
    a = open((macrotarget)+'/'+'atomnotext.txt', 'r')
    atomcontent = a.readlines()
    atom=str((atomcontent[0]).strip('\n'))
    atom=int(atom)
    a.close()
    _safe_remove((macrotarget)+'/'+'atomnotext.txt')
    i=0
    for i in range (0,atom):
      
        yasara.run("BFactorAtom "+str(i+1)+","+str(i+1))
        bfactor=yasara.run("BFactorAtom "+str(i+1))
        if i == 0:
          val= open(macrotarget+'/'+'bfactor.txt','w')
          val.write(str(bfactor).replace('[','').replace(']','').replace('.0',''))
          val.close()
        else:
          valread=open(macrotarget+'/'+'bfactor.txt','r')
          value=valread.readlines()
          valread.close()
          rewrite=open(macrotarget+'/'+'bfactor.txt','w')
          rewrite.writelines(value)
          rewrite.write('\n')
          rewrite.write(str(bfactor).replace('[','').replace(']',''))
          rewrite.close()
        
        i=i+1

    yasara.run("SaveXYZ 1,"+str(macrotarget)+'/'+"QM.xyz,transform=Yes") 


    #yasara.run('ForceField AMBER03,SetPar=Yes')
###charge of the reactant molecule
    #chargeinfo=yasara.run('ChargeObj all')
    yasara.run('JoinObj all,1')
    yasara.run('SaveSMILES 1 ,'+macrotarget+'/'+str(nameobj)+'.smiles,transform=Yes')
    yasara.ShowMessage("Charge calculation is in process...")
    time.sleep(5)    
    smi=open(macrotarget+"/"+str(nameobj)+".smiles","r")
    smidata=smi.read()
    smi.close()
    mol=_require_molecule_from_smiles(smidata)
    chargeinfo=Chem.GetFormalCharge(mol)    
    cfmod=open(macrotarget+'/'+str(nameobj)+'charge.log','w')
    cfmod.write(str(chargeinfo).replace('Summed up net charge is ','').replace('[','').replace(']','').replace(',','\n'))
    cfmod.close()
    chargef= open(macrotarget+'/'+str(nameobj)+'charge.log','r')
    chargeall=chargef.readlines()
    chargef.close()
    charge=float((chargeall[0]).strip('\n'))
    charge=round(charge)
    print(charge)
    alllist =\
      yasara.ShowWin("Custom","INFORMATION",400,250,
      "NumberInput", 20, 88,"Charge",str(charge),-1000,1000,
      "NumberInput", 180, 88,"Multiplicity",1,1,1000,
      "Button",      150,200," O K")  
##counting the object present in the yasara window
    rcharge=open(macrotarget+'/'+str(nameobj)+'charge.log','w+')
    rcharge.write((str(alllist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
    rcharge.close()
    if os.path.getsize(macrotarget+'/'+str(nameobj)+'charge.log') == 0:
      yasara.ShowMessage("Charge calculation failed, restart the process") 
      _safe_remove(macrotarget+'/'+str(nameobj)+'charge.log')
      yasara.plugin.end() 
    else:
      print('ok')   

    react_charge = open(macrotarget+'/'+str(nameobj)+'charge.log', "r")
    reactinfo= react_charge.readlines()
    react_charge.close()
    reactcharge= str((reactinfo[0]).strip('\n'))    
    reactmultiplicity= str((reactinfo[1]).strip('\n')) 

    #f= open(macrotarget+'/'+'QM_res.xyz','r')
    #content= f.readlines()
    #conregion= str(content[0].strip('\n'))
    #print(conregion)
    #x=int(conregion)
    #i=0
    #g= open (macrotarget+'/'+'check.inp','w')
   # for i in range (0, x):
      # g.write('{C ')
      # g.write(str(i))
      # g.write(' C}\n')
      # i=i+1
   # g.close()
  
    with open(str(macrotarget)+'/'+'QM.xyz', 'r') as fin:
        data = fin.read().splitlines(True)
    with open(str(macrotarget)+'/'+'qm.txt', 'w') as fout:
        fout.writelines(data[2:]) 
        fout.close()
     
    orcaproinp=open((macrotarget)+'/'+'qm.txt')
    prodata=orcaproinp.read()
    orcaproinp.close()

    con=open((macrotarget)+'/'+'check.inp')
    condata=con.read()
    con.close()
    if functionalqm2 == 'XTB' or functionalqm2== 'PM3':
      k= open(macrotarget+'/'+'QM_reactant.inp','w')
      k.write('! QM/')
      k.write(str(functionalqm2))
      k.write(' ')
      k.write(str(basisqm2))
      k.write(' ')
      k.write(str(functional))
      k.write(' ')
      k.write(str(basis))
      k.write(' Opt\n')
      k.write('%QMMM QMATOMS {')
      k.write(str(condata))
      k.write('} END END')
      k.write('\n%maxcore 101376\n%geom')    
      k.write('\nend')
      #k.write("\n%pal\n   nprocs ")
     # k.write(str(processor))
      #k.write('\nend\n')
      k.write('\n*xyz ')
      k.write(str(reactcharge))
      k.write(' ')
      k.write(str(reactmultiplicity))
      k.write('\n')
      k.write(str(prodata))
      k.write('\n*')
      k.close()
    else:
      k= open(macrotarget+'/'+'QM_reactant.inp','w')
      k.write('! QM/QM2 ')
      k.write(str(functional))
      k.write(' ')
      k.write(str(basis))
      k.write(' Opt\n')
      k.write('%QMMM QM2CUSTOMMETHOD "')
      k.write(str(functionalqm2))
      k.write(' ')
      k.write(str(basisqm2))
      k.write('"\n      QMATOMS {')
      k.write(str(condata))
      k.write('} END END')
      k.write('\n%maxcore 101376\n%geom')    
      k.write('\nend')
      #k.write("\n%pal\n   nprocs ")
      #k.write(str(processor))
      #k.write('\nend\n')
      k.write('\n*xyz ')
      k.write(str(reactcharge))
      k.write(' ')
      k.write(str(reactmultiplicity))
      k.write('\n')
      k.write(str(prodata))
      k.write('\n*')
      k.close()        

    os.chdir(pathYasara)
    os.chdir(macrotarget)  
    yasara.ShowMessage("Geometry optimization is in progress..")  
    if mod == str(1) or mod == str(2): 
      print('check')
      _run_legacy_command(orca+' QM_reactant.inp >QM_reactant.out')
    else:
      _run_legacy_command('orca QM_reactant.inp >QM_reactant.out')


    yasara.run('DelObj all')
    if os.path.isfile(macrotarget+'/'+'QM_reactant.xyz'):
      yasara.run('LoadXYZ '+macrotarget+'/'+'QM_reactant.xyz')
    else:
      yasara.ShowMessage("Geometry optimization failed") 

    transitionlist =\
      yasara.ShowWin("Custom","Transition state",400,250,
       "Text", 20, 50, "Do you want to perform transition state?",
       "RadioButtons",2,1,
                      20, 100,"yes",
                      200,100,"no",
       "Button",      150,200," O K")
    tsattach= open((macrotarget)+'/'+'ts_ini.txt','w+')
    tsattach.write((str(transitionlist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
    tsattach.close()  
    fts = open((macrotarget)+'/'+'ts_ini.txt', "r")
    contentts= fts.readlines()
    fts.close()
    ats = str((contentts[0]).strip('\n'))    
    if ats == str(2) or mod==str(2):
       yasara.ShowMessage("Geometry optimization is complete. For ONIOM TS calculation, XTB tool is required.")
       print('XTB is currently available only for linux system..in absent of XTB, GUIDE can not perform ONIOM TS calculation.')
       yasara.plugin.end()
    yasara.ShowMessage("Make sure XTB is installed and otool_xtb is present in Orca directory")
    print('XTB is currently available only for linux system..in absent of XTB, GUIDE can not perform ONIOM TS calculation.')
    yasara.run("wait continuebutton")
    imgalllist =\
        yasara.ShowWin("Custom","No of points",400,250,
       "Text",        50, 50,"*Select the  total number of reaction point",
       "NumberInput", 20, 80,"points",8,8,100,
        "Button",      150,200," O K")  
##counting the object present in the yasara window
    rimg=open(macrotarget+'/'+str(nameobj)+'images.log','w+')
    rimg.write((str(imgalllist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
    rimg.close()
    if os.path.getsize(macrotarget+'/'+str(nameobj)+'images.log') == 0:
      yasara.ShowMessage("QM calculation failed. Must need the number of reaction points. Please restart the process") 
      _safe_remove(macrotarget+'/'+str(nameobj)+'procharge.log')
      yasara.plugin.end() 

    img = open(macrotarget+'/'+str(nameobj)+'images.log', "r")
    noimg= img.readlines()
    img.close()
    numeroimg= str((noimg[0]).strip('\n')) 

    i=0
    for i in range (0,atom):
      
        yasara.run("BFactorAtom "+str(i+1)+","+str(i+1))
        bfactor=yasara.run("BFactorAtom "+str(i+1))
        if i == 0:
          val= open(macrotarget+'/'+'bfactor.txt','w')
          val.write(str(bfactor).replace('[','').replace(']','').replace('.0',''))
          val.close()
        else:
          valread=open(macrotarget+'/'+'bfactor.txt','r')
          value=valread.readlines()
          valread.close()
          rewrite=open(macrotarget+'/'+'bfactor.txt','w')
          rewrite.writelines(value)
          rewrite.write('\n')
          rewrite.write(str(bfactor).replace('[','').replace(']',''))
          rewrite.close()
        
        i=i+1
   
##concatination of reactant xyz info with its b-factor value   
    combine =[]

    with open((macrotarget)+'/'+'bfactor.txt') as xh:
      with open((macrotarget)+'/'+'qm.txt') as yh:
        with open((macrotarget)+'/'+'QM_filter.txt',"w") as zh:
         #Read first file
           xlines = xh.readlines()
         #Read second file
           ylines = yh.readlines()
         #Combine content of both lists
         #combine = list(zip(ylines,xlines))
         #Write to third file
           for i in range(len(xlines)):
              line = ylines[i].strip('\n') + '    ' + xlines[i]
              zh.write(line)
#_safe_remove((macrotarget)+'/'+'reactant.txt')
    #_safe_remove((macrotarget)+'/'+'bfactor.txt')
    #yasara.run("DuplicateAll")
    #yasara.run("DelObj 1")
    yasara.run('BallStickObj all')
    yasara.run("LabelAll 'Do not update hydrogen after bond modification',Height=1.9,Color=Yellow,X=0,Y=19,Z=65")
    yasara.ShowMessage("Please modify the reactant to build product molecule and then click continue")
    yasara.run("wait continuebutton")
    yasara.run('SelectAtom L')
    #yasara.run('FixAtom selected')
    yasara.ShowMessage("Geometry optimization is in progress..") 
    #yasara.run('UnselectAll')
    #yasara.run('Cell Auto,Shape=Cube,selected')
    yasara.run('UnselectAll')
    #yasara.ExperimentMinimization()
    #yasara.Experiment("On")
    #yasara.Wait("ExpEnd")
    #yasara.run('DelObj simcell')
    yasara.run('InflateObj all')
    yasara.run('DeflateAll')
    yasara.run('InflateAll')
    yasara.ShowMessage("Charge calculation is in progress..")
##Calculating the charge of the product
    #prochargeinfo=yasara.run('ChargeObj all')
    yasara.run('JoinObj all,1')
    yasara.run('SaveSMILES 1 ,'+macrotarget+'/'+str(nameobj)+'.smiles,transform=Yes')
    yasara.ShowMessage("Charge calculation is in process...")
    time.sleep(5)    
    smi=open(macrotarget+"/"+str(nameobj)+".smiles","r")
    smidata=smi.read()
    smi.close()
    mol=_require_molecule_from_smiles(smidata)
    prochargeinfo=Chem.GetFormalCharge(mol)    
    promod=open(macrotarget+'/'+str(nameobj)+'procharge.log','w')
    promod.write(str(prochargeinfo).replace('Summed up net charge is ','').replace('[','').replace(']',''))
    promod.close()
    prochargef= open(macrotarget+'/'+str(nameobj)+'procharge.log','r')
    prochargeall=prochargef.readlines()
    prochargef.close()
    procharge=float((prochargeall[0]).strip('\n'))
    procharge=round(procharge)
    print(procharge)

    proalllist =\
      yasara.ShowWin("Custom","INFORMATION",400,250,
      "NumberInput", 20, 88,"Charge",str(procharge),-1000,1000,
      "NumberInput", 180, 88,"Multiplicity",1,1,1000,
      "Button",      150,200," O K")  
##counting the object present in the yasara window
    pcharge=open(macrotarget+'/'+str(nameobj)+'procharge.log','w+')
    pcharge.write((str(proalllist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
    pcharge.close()

    if os.path.getsize(macrotarget+'/'+str(nameobj)+'procharge.log') == 0:
      yasara.ShowMessage("Charge calculation failed, restart the process") 
      _safe_remove(macrotarget+'/'+str(nameobj)+'procharge.log')
      yasara.plugin.end() 
    else:
      print('ok')   
    pro_charge = open(macrotarget+'/'+str(nameobj)+'procharge.log', "r")
    productinfo= pro_charge.readlines()
    pro_charge.close()
    productcharge= str((productinfo[0]).strip('\n'))    
    productmultiplicity= str((productinfo[1]).strip('\n')) 


  ##counting the atom of product present in the yasara window
    proatom=yasara.run("Countatom all")
    prodeltext= open(macrotarget+'/'+'prodeltext.txt','w')
    prodeltext.write(str(proatom).replace('atom(s) match the selection.','').replace('[','').replace(']',''))
    prodeltext.close()
    p = open((macrotarget)+'/'+'prodeltext.txt', "r")
    pcontent = p.readlines()
    nopro=str((pcontent[0]).strip('\n').strip('[').strip(']'))
    p.close()
    atom=str(atom)
    _safe_remove((macrotarget)+'/'+'prodeltext.txt')
##checking the number of atom in product and reactant are same or not

    if nopro == atom :
      #yasara.run('JoinObj all,1')
      j=0
      nopro=int(nopro)
      for j in range (0,nopro):
          bfactor=yasara.run("BFactorAtom "+str(j+1))
          if j == 0:
            val= open(macrotarget+'/'+'product_bfactor.txt','w')
            val.write(str(bfactor).replace('[','').replace(']','').replace('.0',''))
            val.close()
          else:
            valread=open(macrotarget+'/'+'product_bfactor.txt','r')
            value=valread.readlines()
            valread.close()
            rewrite=open(macrotarget+'/'+'product_bfactor.txt','w')
            rewrite.writelines(value)
            rewrite.write('\n')
            rewrite.write(str(bfactor).replace('[','').replace(']','').replace('.0',''))
            rewrite.close()
        
          j=j+1 
    else:
     yasara.ShowMessage("WARNING! please see the terminal")
     print(nopro)
     print(atom)
     print("No. of atoms must be same for reactant and product")
     yasara.plugin.end()        


##Saving the xyz file of the product
    yasara.run("SaveXYZ all,"+str(macrotarget)+'/'+"QM_product.xyz,transform=Yes") 
    time.sleep(5)
##modifying the reactant.xyz file without hamparing the main file
    with open(str(macrotarget)+'/'+'QM_product.xyz', 'r') as fin:
        data = fin.read().splitlines(True)
    with open(str(macrotarget)+'/'+'QM_product.txt', 'w') as fout:
        fout.writelines(data[2:]) 
        fout.close()
   
##concatination of reactant xyz info with its b-factor value   
    procombine =[]

    with open((macrotarget)+'/'+'QM_product.txt') as xh:
      with open((macrotarget)+'/'+'product_bfactor.txt') as yh:
        with open((macrotarget)+'/'+'QM_product_filter.txt',"w") as zh:
       #Read first file
           xlines = xh.readlines()
         #Read second file
           ylines = yh.readlines()
         #Combine content of both lists
         #combine = list(zip(ylines,xlines))
         #Write to third file
           for i in range(len(xlines)):
              line = ylines[i].strip('\n') + '    ' + xlines[i]
              zh.write(line)

    yasara.run("clear")
    yasara.run("DelObj all")
    yasara.run('Loadxyz '+macrotarget+'/'+'QM.xyz')
    yasara.run('BallStickObj all')
    yasara.run('Loadxyz '+macrotarget+'/'+'QM_product.xyz')
    yasara.run('BallStickObj all')
    radius=yasara.run('RadiusObj 1')
    rd=open(macrotarget+'/'+'radius.txt','w+')
    rd.write(str(radius).replace('[','').replace(']','').replace('Object  1 (reactant) has a VdW radius of ','').replace('A from its geometric center',''))
    rd.close()
    fk=open(macrotarget+'/'+'radius.txt','r')
    r=fk.readline()
    fk.close()
    r=str(r)
    r=float(r)
    display_offset = 15
    y = r + display_offset
    y=str(y)
    z = -r - display_offset
    z=str(z)
#yasara.run('r=RadiusObj 1')
#yasara.run('len=15')
    yasara.run('MoveObj !1,X='+str(y))
    yasara.run('MoveObj 1,X='+str(z))
    yasara.run('ShowArrow Start=Point,X=-15,Y=0,Z=50,End=Point,X=15,Y=0,Z=50,Radius=1,Color=Yellow')
    yasara.run('ZoomAll Steps=0')
    yasara.run('Move Z=20')
    yasara.run('LabelObj 1,reactant,Color=Yellow,Y=5,Z=-5')
    yasara.run('LabelObj 2,product,Color=Yellow,Y=5,Z=-5')

    def sortLinesByColumn(readable, column, columnt_type):
        """Returns a list of strings (lines in readable file) in sorted order (based on column)"""
        lines = []

        for line in readable:
            # get the element in column based on which the lines are to be sorted
            column_element= columnt_type(line.split(' ')[column-1])
            lines.append((column_element, line))

        lines.sort()

        return [x[1] for x in lines]


    with open((macrotarget)+'/'+'QM_product_filter.txt') as f:
        # sort the lines based on column 1, and column 1 is type int
        sorted_lines = sortLinesByColumn(f, 1, int)
        k= open((macrotarget)+'/'+'QM_product_final.txt',"w")
        k.writelines(sorted_lines)
        k.close()

  #_safe_remove((macrotarget)+'/'+'product_filter.txt')
    proedit = open((macrotarget)+'/'+'QM_product_final.txt', "r")
    editfile = open((macrotarget)+'/'+'QM_product_filter.txt', "w")
    for line in proedit:
        if line.strip():
            editfile.write("\t".join(line.split()[1:]) + "\n")    
    proedit.close()
    editfile.close()
    _safe_remove((macrotarget)+'/'+'QM_product_final.txt')


    qmorcaproinp=open((macrotarget)+'/'+'QM_product_filter.txt')
    qmprodata=qmorcaproinp.read()
    qmorcaproinp.close()
    print(prodata)
    if functionalqm2 == 'XTB' or functionalqm2== 'PM3':
      orca_geo_pro=open((macrotarget)+'/'+'QM_product.inp','w+')
      orca_geo_pro.write("! QM/")
      orca_geo_pro.write(str(functionalqm2))
      orca_geo_pro.write(' ')
      orca_geo_pro.write(str(basisqm2))
      orca_geo_pro.write(' ')
      orca_geo_pro.write(str(functional))
      orca_geo_pro.write(" ")
      orca_geo_pro.write(str(basis))
      orca_geo_pro.write(' Opt\n')
    #orca_geo_pro.write("\n%pal\n   nprocs ")
    #orca_geo_pro.write(str(processor))
    #orca_geo_pro.write('\nend')
      orca_geo_pro.write('%QMMM QMATOMS {')
      orca_geo_pro.write(str(condata))
      orca_geo_pro.write('} END END')
      orca_geo_pro.write('\n%maxcore 101376\n%geom')
      orca_geo_pro.write('\nend')
      #orca_geo_pro.write("\n%pal\n   nprocs ")
      #orca_geo_pro.write(str(processor))
      #orca_geo_pro.write('\nend\n')
      orca_geo_pro.write('\n*xyz ')    
      orca_geo_pro.write(str(productcharge))
      orca_geo_pro.write(" ")
      orca_geo_pro.write(str(productmultiplicity))
      orca_geo_pro.write("\n")
  #orca_geo_pro.write(str(reactdata))
      orca_geo_pro.write(str(qmprodata))
      orca_geo_pro.write("\n*")
      orca_geo_pro.close()
    else:
      orca_geo_pro=open((macrotarget)+'/'+'QM_product.inp','w+')
      orca_geo_pro.write("! QM/QM2 ")
      #orca_geo_pro.write(str(functionalqm2))
      #orca_geo_pro.write(' ')
      #orca_geo_pro.write(str(basisqm2))
      #orca_geo_pro.write(' ')
      orca_geo_pro.write(str(functional))
      orca_geo_pro.write(" ")
      orca_geo_pro.write(str(basis))
      orca_geo_pro.write(' Opt\n')
    #orca_geo_pro.write("\n%pal\n   nprocs ")
    #orca_geo_pro.write(str(processor))
    #orca_geo_pro.write('\nend')
      orca_geo_pro.write('%QMMM QM2CUSTOMMETHOD "')
      orca_geo_pro.write(str(functionalqm2))
      orca_geo_pro.write(' ')
      orca_geo_pro.write(str(basisqm2))  
      orca_geo_pro.write('"\n      QMATOMS {')
      orca_geo_pro.write(str(condata))
      orca_geo_pro.write('} END END')
      orca_geo_pro.write('\n%maxcore 101376\n%geom')
      orca_geo_pro.write('\nend')
      #orca_geo_pro.write("\n%pal\n   nprocs ")
      #orca_geo_pro.write(str(processor))
      #orca_geo_pro.write('\nend\n')
      orca_geo_pro.write('\n*xyz ')    
      orca_geo_pro.write(str(productcharge))
      orca_geo_pro.write(" ")
      orca_geo_pro.write(str(productmultiplicity))
      orca_geo_pro.write("\n")
  #orca_geo_pro.write(str(reactdata))
      orca_geo_pro.write(str(qmprodata))
      orca_geo_pro.write("\n*")
      orca_geo_pro.close()      



    yasara.ShowMessage("Geometry optimization is in progress..")  
    if mod == str(1) or mod == str(2): 
      print('check')
      _run_legacy_command(orca+' QM_product.inp >QM_product.out')
    else:
      _run_legacy_command('orca QM_product.inp >QM_product.out')




    yasara.ShowMessage("Geometry optimization is complete")
    if functionalqm2 == 'XTB' or functionalqm2== 'PM3':
      tsinp=open((macrotarget)+'/'+'ts.inp','w+')
      tsinp.write('!QM/')
      tsinp.write(str(functionalqm2))
      tsinp.write(' ')
      tsinp.write(str(basisqm2))
      tsinp.write(' ')
      tsinp.write(str(functional))
      tsinp.write(' ')
      tsinp.write(str(basis))
      tsinp.write(' NEB-TS NUMFREQ \n')#FREQ')
      tsinp.write('%QMMM QMATOMS {')
      tsinp.write(str(condata))
      tsinp.write('} END END')    
      tsinp.write('\n%NEB PREOPT TRUE PRODUCT "QM_product.xyz" \n')   
      tsinp.write('\nNImages ')
      tsinp.write(str(numeroimg))
      tsinp.write('\n\nend ')
      #tsinp.write("\n\n%pal\n   nprocs ")
      #tsinp.write(str(processor))
      #tsinp.write('\nend')         
      tsinp.write('\n*XYZFILE ')
      tsinp.write(str(reactcharge))
      tsinp.write(' ')
      tsinp.write(str(reactmultiplicity))
      tsinp.write(' QM_reactant.xyz\n\n')
      tsinp.close()
    else:
      tsinp=open((macrotarget)+'/'+'ts.inp','w+')
      tsinp.write('!QM/QM2 ')
      #tsinp.write(str(functionalqm2))
      #tsinp.write(' ')
      #tsinp.write(str(basisqm2))
      #tsinp.write(' ')
      tsinp.write(str(functional))
      tsinp.write(' ')
      tsinp.write(str(basis))
      tsinp.write(' NEB-TS  NUMFREQ\n')#FREQ')
      tsinp.write('%QMMM QM2CUSTOMMETHOD "')
      tsinp.write(str(functionalqm2))
      tsinp.write(' ')
      tsinp.write(str(basisqm2))      
      tsinp.write('"\n      QMATOMS {')
      tsinp.write(str(condata))
      tsinp.write('} END END')    
      tsinp.write('\n%NEB PREOPT TRUE PRODUCT "QM_product.xyz" \n')   
      tsinp.write('\nNImages ')
      tsinp.write(str(numeroimg))
      tsinp.write('\n\nend ')
      #tsinp.write("\n\n%pal\n   nprocs ")
      #tsinp.write(str(processor))
      #tsinp.write('\nend')         
      tsinp.write('\n*XYZFILE ')
      tsinp.write(str(reactcharge))
      tsinp.write(' ')
      tsinp.write(str(reactmultiplicity))
      tsinp.write(' QM_reactant.xyz\n\n')
      tsinp.close()      
    yasara.ShowMessage("Transition state calculation is in process..")
    os.chdir(pathYasara)
    os.chdir(macrotarget)
    time.sleep(5)
    if mod == str(1) or mod == str(2): 
      _run_legacy_command(orca+' ts.inp >ts.out')
    else:
      _run_legacy_command('orca ts.inp >ts.out')

    if os.path.isfile(macrotarget+'/'+'ts_MEP_trj.xyz') :
      trjlist =\
        yasara.ShowWin("Custom","Trjectory view",400,250,
         "Text", 20, 50, "Do you want to visualize trajectory?",
         "RadioButtons",2,1,
                        20, 100,"yes",
                        200,100,"no",
         "Button",      150,200," O K")
      attach= open((macrotarget)+'/'+'trjectory.txt','w+')
      attach.write((str(trjlist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
      attach.close()  
      f = open((macrotarget)+'/'+'trjectory.txt', "r")
      content= f.readlines()
      f.close()
      a = str((content[0]).strip('\n'))   
      if a == str(1):
        if mod == str(1):
          _safe_move(macrotarget+'/'+'ts_MEP_trj.xyz', macrotarget+'/'+'ts_MEP_final.xyz' )
        else:
           _safe_move(macrotarget+'/'+'ts_MEP_trj.xyz', macrotarget+'/'+'ts_MEP_final.xyz' )     
    
        yasara.run('DelObj all')  
        yasara.run('Loadxyz '+macrotarget+'/'+'ts_MEP_final.xyz')
        yasara.run('BallStickObj all')
        obj=yasara.run("CountObj all")
        deltext= open(macrotarget+'/'+'deltext.txt','w')
        deltext.write(str(obj).replace('object(s) match the selection.','').replace('[','').replace(']',''))
        deltext.close()
        g = open((macrotarget)+'/'+'deltext.txt', "r")
        content = g.readlines()
        noobj=str((content[0]).strip('\n'))
        g.close()
        noobj=int(noobj)
        k=0
        yasara.run('ZoomAll Steps=20')
        yasara.run('HideObj all')
        for k in range(0,noobj):
            yasara.run('ShowObj '+str(k+1))
            yasara.run('BallStickObj all')
            yasara.run("wait continuebutton")
            if int(k+1) == noobj :
              print('done')
            else:
              yasara.run('DelObj '+str(k+1))
            k=k+1
        yasara.ShowMessage("Transition state calculation is complete and results are saved in: "+ macrotarget)
  
    else:
      yasara.ShowMessage("Transition state calculation is complete and results are saved in: "+ macrotarget)    




###QM-MM region########################################################## 
  else :
    yasara.ShowMessage("Please load Your structure")
    print(functional)
    print(basis)
    yasara.run("wait continuebutton")
    yasara.run("JoinObj all,1")
    
    yasara.run("SavePDB 1,"+str(macrotarget)+"/"+"MM.pdb")
    yasara.ShowMessage("Please select QM object(s) and then click continue")
    yasara.run("wait continuebutton")
    #yasara.run("JoinRes Selected")
    ####have to check
    yasara.run("NameAtom Selected,L")
    #yasara.run("NameAtom all and not selected, con")
    yasara.ShowMessage("Please additionally select atoms for constraining")
    yasara.run("wait continuebutton")
    #yasara.run("UnselectAll")
    #yasara.run("SelectAtom all with distance < 1 from L")
    ####have to check
    yasara.run("DelAtom all !selected")
    yasara.run("UnselectAll")
    yasara.run("SelectAtom all and not L")
    yasara.run("NameRes selected,con")
    yasara.run("AddHydRes con")
    print('check###')
    yasara.run('BFactorAtom all,0')
    #yasara.run("wait continuebutton")
    countobj=yasara.run('CountObj all')

    #yasara.run("wait continuebutton")
    #yasara.run('joinObj all,1')    
    yasara.run("SavePDB all,"+str(macrotarget)+'/'+"QM.pdb,transform=Yes") 
    #yasara.run("SaveXYZ 1,"+str(macrotarget)+'/'+"QM.xyz,transform=Yes") 
    yasara.run('BFactorAtom all,0')
    cnoatom=yasara.run("CountAtom all")
    catomtext= open(macrotarget+'/'+'catomnotext.txt','w')
    catomtext.write(str(cnoatom).replace('atom(s) match the selection.','').replace('[','').replace(']',''))
    catomtext.close()
    ca = open((macrotarget)+'/'+'catomnotext.txt', 'r')
    catomcontent = ca.readlines()
    catom=str((catomcontent[0]).strip('\n'))
    catom=int(catom)
    ca.close()
    _safe_remove((macrotarget)+'/'+'catomnotext.txt')
    ci=0
    for ci in range (0,catom):
      
        yasara.run("BFactorAtom "+str(ci+1)+","+str((ci+1)-1))
        
    ci=ci+1
    yasara.run("DelAtom L")

     
    bfactor=yasara.run("BFactorAtom all")
    
    yasara.ShowMessage("Charge calculation is in progress..")
    resnoatom=yasara.run("CountAtom all")
    resatomtext= open(macrotarget+'/'+'resatomnotext.txt','w')
    resatomtext.write(str(resnoatom).replace('atom(s) match the selection.','').replace('[','').replace(']',''))
    resatomtext.close()
    resa = open((macrotarget)+'/'+'resatomnotext.txt', 'r')
    resatomcontent = resa.readlines()
    resatom=str((resatomcontent[0]).strip('\n'))
    resatom=int(resatom)
    resa.close()
    _safe_remove((macrotarget)+'/'+'resatomnotext.txt')
    resi=0
    for i in range (0,resatom):
      
        #yasara.run("BFactorAtom "+str(resi+1)+","+str(resi+1))
        resbfactor=yasara.run("BFactorAtom "+str(resi+1))
        if i == 0:
          val= open(macrotarget+'/'+'check.inp','w')
          val.write("{C ")
          val.write(str(resbfactor).replace('[','').replace(']','').replace('.0',''))
          val.write(" C}")
          val.close()
        else:
          valread=open(macrotarget+'/'+'check.inp','r')
          value=valread.readlines()
          valread.close()
          rewrite=open(macrotarget+'/'+'check.inp','w')
          rewrite.writelines(value)
          rewrite.write('\n')
          rewrite.write('{C ')
          rewrite.write(str(resbfactor).replace('[','').replace(']','').replace('.0',''))
          rewrite.write(' C}')
          rewrite.close()
        
        resi=resi+1

    #yasara.run('joinAtom all,1') 
    yasara.run("SaveXYZ all,"+str(macrotarget)+'/'+"QM_res.xyz,transform=Yes")  
    yasara.run("DelObj all")
    yasara.run('LoadPDB '+macrotarget+'/'+'QM.pdb')
    yasara.run('AddHydAll')
    time.sleep(3)
    yasara.run('SaveSMILES 1 ,'+macrotarget+'/'+str(nameobj)+'.smiles,transform=Yes')
    time.sleep(3)
    yasara.run('BFactorAtom all,0')
    noatom=yasara.run("CountAtom all")
    atomtext= open(macrotarget+'/'+'atomnotext.txt','w')
    atomtext.write(str(noatom).replace('atom(s) match the selection.','').replace('[','').replace(']',''))
    atomtext.close()
    a = open((macrotarget)+'/'+'atomnotext.txt', 'r')
    atomcontent = a.readlines()
    atom=str((atomcontent[0]).strip('\n'))
    atom=int(atom)
    a.close()
    _safe_remove((macrotarget)+'/'+'atomnotext.txt')
    i=0
    for i in range (0,atom):
      
        yasara.run("BFactorAtom "+str(i+1)+","+str(i+1))
        bfactor=yasara.run("BFactorAtom "+str(i+1))
        if i == 0:
          val= open(macrotarget+'/'+'bfactor.txt','w')
          val.write(str(bfactor).replace('[','').replace(']','').replace('.0',''))
          val.close()
        else:
          valread=open(macrotarget+'/'+'bfactor.txt','r')
          value=valread.readlines()
          valread.close()
          rewrite=open(macrotarget+'/'+'bfactor.txt','w')
          rewrite.writelines(value)
          rewrite.write('\n')
          rewrite.write(str(bfactor).replace('[','').replace(']',''))
          rewrite.close()
        
        i=i+1

    yasara.run("SaveXYZ 1,"+str(macrotarget)+'/'+"QM.xyz,transform=Yes") 


    #yasara.run('ForceField AMBER03,SetPar=Yes')
###charge of the reactant molecule
    #chargeinfo=yasara.run('ChargeObj all')
    yasara.run('JoinObj all,1')
    #yasara.run('SaveSMILES 1 ,'+macrotarget+'/'+str(nameobj)+'.smiles,transform=Yes')
    yasara.ShowMessage("Charge calculation is in process...")
    time.sleep(5)    
    smi=open(macrotarget+"/"+str(nameobj)+".smiles","r")
    smidata=smi.read()
    smi.close()
    mol=_require_molecule_from_smiles(smidata)
    chargeinfo=Chem.GetFormalCharge(mol)    
    cfmod=open(macrotarget+'/'+str(nameobj)+'charge.log','w')
    cfmod.write(str(chargeinfo).replace('Summed up net charge is ','').replace('[','').replace(']','').replace(',','\n'))
    cfmod.close()
    chargef= open(macrotarget+'/'+str(nameobj)+'charge.log','r')
    chargeall=chargef.readlines()
    chargef.close()
    charge=float((chargeall[0]).strip('\n'))
    charge=round(charge)
    print(charge)
    alllist =\
      yasara.ShowWin("Custom","INFORMATION",400,250,
      "NumberInput", 20, 88,"Charge",str(charge),-1000,1000,
      "NumberInput", 180, 88,"Multiplicity",1,1,1000,
      "Button",      150,200," O K")  
##counting the object present in the yasara window
    rcharge=open(macrotarget+'/'+str(nameobj)+'charge.log','w+')
    rcharge.write((str(alllist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
    rcharge.close()
    if os.path.getsize(macrotarget+'/'+str(nameobj)+'charge.log') == 0:
      yasara.ShowMessage("Charge calculation failed, restart the process") 
      _safe_remove(macrotarget+'/'+str(nameobj)+'charge.log')
      yasara.plugin.end() 
    else:
      print('ok')   

    react_charge = open(macrotarget+'/'+str(nameobj)+'charge.log', "r")
    reactinfo= react_charge.readlines()
    react_charge.close()
    reactcharge= str((reactinfo[0]).strip('\n'))    
    reactmultiplicity= str((reactinfo[1]).strip('\n')) 

    f= open(macrotarget+'/'+'QM_res.xyz','r')
    content= f.readlines()
    f.close()
    conregion= str(content[0].strip('\n'))
    print(conregion)
    x=int(conregion)
    #i=0
    #g= open (macrotarget+'/'+'check.inp','w')
   # for i in range (0, x):
      # g.write('{C ')
      # g.write(str(i))
      # g.write(' C}\n')
      # i=i+1
   # g.close()
  
    with open(str(macrotarget)+'/'+'QM.xyz', 'r') as fin:
        data = fin.read().splitlines(True)
    with open(str(macrotarget)+'/'+'qm.txt', 'w') as fout:
        fout.writelines(data[2:]) 
        fout.close()
     
    orcaproinp=open((macrotarget)+'/'+'qm.txt')
    prodata=orcaproinp.read()
    orcaproinp.close()

    con=open((macrotarget)+'/'+'check.inp')
    condata=con.read()
    con.close()
    k= open(macrotarget+'/'+'QM_reactant.inp','w')
    k.write('! SP ')
    k.write(str(functional))
    k.write(' ')
    k.write(str(basis))
    k.write(' Opt Mulliken')
   # k.write("\n%pal\n   nprocs ")
  #  k.write(str(processor))
   # k.write('\nend')
    k.write('\n%maxcore 101376\n%geom \nConstraints\n')
    k.write(str(condata))
    k.write('\nend\nend\n*xyz ')
    k.write(str(reactcharge))
    k.write(' ')
    k.write(str(reactmultiplicity))
    k.write('\n')
    k.write(str(prodata))
    k.write('\n*')
    k.close()
    os.chdir(pathYasara)
    os.chdir(macrotarget)  
    yasara.ShowMessage("Geometry optimization is in progress..")  
    if mod == str(1): 
      print('check')
      _run_legacy_command(orca+' '+macrotarget+'/'+'QM_reactant.inp >' +macrotarget+'/'+'QM_reactant.out')
    elif mod == str(2):
      nameobj='QM_reactant'
      
      print(nameobj)
      _run_legacy_command(orca+' '+macrotarget+'/'+str(nameobj)+'.inp >  '+macrotarget+'/'+str(nameobj)+'.out')
    else:
      _run_legacy_command('orca QM_reactant.inp >QM_reactant.out')



    yasara.run('DelObj all')
    if os.path.isfile(macrotarget+'/'+'QM_reactant.xyz'):
      yasara.run('LoadXYZ '+macrotarget+'/'+'QM_reactant.xyz')
    else:
      yasara.ShowMessage("Geometry optimization failed") 
    transitionlist =\
      yasara.ShowWin("Custom","Calculation",400,250,
       "Text", 20, 50, "Do you want to perform other calculations?",
       "RadioButtons",2,1,
                      20, 100,"yes",
                      200,100,"no",
       "Button",      150,200," O K")
    tsattach= open((macrotarget)+'/'+'ts_ini.txt','w+')
    tsattach.write((str(transitionlist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
    tsattach.close()  
    fts = open((macrotarget)+'/'+'ts_ini.txt', "r")
    contentts= fts.readlines()
    fts.close()
    ats = str((contentts[0]).strip('\n'))    
    if ats == str(2):
       yasara.ShowMessage("Geometry optimization is complete")
       yasara.plugin.end()


###########################################
    recalculationlist=\
      yasara.ShowWin("Custom","CALCULATION",400,250,
      "Text", 20, 48, "Calculation type",
      "RadioButtons",2,1,
                     20, 105,"HOMO-LUMO energy gap",
                     20, 155,"Fukui function",
      "Button",      150,200," O K")    


    recal=open(macrotarget+'/'+'recalculation.txt','w+')
    recal.write((str(recalculationlist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
    recal.close()
    methos_recal = open(macrotarget+'/'+'recalculation.txt', "r")
    recaltype= methos_recal.readlines()
    methos_recal.close()
    if os.path.getsize(macrotarget+'/'+'recalculation.txt') == 0:
      yasara.ShowMessage("QM calculation failed, select a specific method") 
      _safe_remove(macrotarget+'/'+'recalculation.txt')
      yasara.plugin.end() 
    else:
      print('ok') 

    remethodology= str((recaltype[0]).strip('\n')) 


############################
    if remethodology == str(3):
      imgalllist =\
          yasara.ShowWin("Custom","No of point",400,250,
          "Text",        50, 50,"*Select the  total number of reaction point",
          "NumberInput", 20, 80,"points",8,8,100,
          "Button",      150,200," O K")  
##counting the object present in the yasara window
      rimg=open(macrotarget+'/'+str(nameobj)+'images.log','w+')
      rimg.write((str(imgalllist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
      rimg.close()
      if os.path.getsize(macrotarget+'/'+str(nameobj)+'images.log') == 0:
        yasara.ShowMessage("QM calculation failed. Must need the number of reaction points. Please restart the process") 
        _safe_remove(macrotarget+'/'+str(nameobj)+'procharge.log')
        yasara.plugin.end() 

      img = open(macrotarget+'/'+str(nameobj)+'images.log', "r")
      noimg= img.readlines()
      img.close()
      numeroimg= str((noimg[0]).strip('\n')) 

      i=0
      for i in range (0,atom):
      
          yasara.run("BFactorAtom "+str(i+1)+","+str(i+1))
          bfactor=yasara.run("BFactorAtom "+str(i+1))
          if i == 0:
            val= open(macrotarget+'/'+'bfactor.txt','w')
            val.write(str(bfactor).replace('[','').replace(']','').replace('.0',''))
            val.close()
          else:
            valread=open(macrotarget+'/'+'bfactor.txt','r')
            value=valread.readlines()
            valread.close()
            rewrite=open(macrotarget+'/'+'bfactor.txt','w')
            rewrite.writelines(value)
            rewrite.write('\n')
            rewrite.write(str(bfactor).replace('[','').replace(']',''))
            rewrite.close()
        
          i=i+1



##concatination of reactant xyz info with its b-factor value   
      combine =[]

      with open((macrotarget)+'/'+'bfactor.txt') as xh:
        with open((macrotarget)+'/'+'qm.txt') as yh:
          with open((macrotarget)+'/'+'QM_filter.txt',"w") as zh:
         #Read first file
             xlines = xh.readlines()
         #Read second file
             ylines = yh.readlines()
         #Combine content of both lists
         #combine = list(zip(ylines,xlines))
         #Write to third file
             for i in range(len(xlines)):
                line = ylines[i].strip('\n') + '    ' + xlines[i]
                zh.write(line)
#_safe_remove((macrotarget)+'/'+'reactant.txt')
    #_safe_remove((macrotarget)+'/'+'bfactor.txt')
    #yasara.run("DuplicateAll")
    #yasara.run("DelObj 1")
      yasara.run('BallStickObj all')
      yasara.run("LabelAll 'Do not update hydrogen after bond modification',Height=1.9,Color=Yellow,X=0,Y=19,Z=65")
    #yasara.ShowMessage("First select the atoms in the structure for modification")
    #yasara.run("wait continuebutton")
   # yasara.run('FixAtom all and not selected')
      yasara.ShowMessage("Please modify the atoms to build product molecule and then click continue")
      yasara.run("wait continuebutton")
      conopen=open(macrotarget+'/'+'check.inp','r')
      conopenread=conopen.read()
      conopen.close()
      conmodi=open(macrotarget+'/'+'constraint_atoms.inp','w+')
      conmodi.write(str(conopenread).replace('{C ','').replace(' C}',''))
      conmodi.close()
      with open(macrotarget+'/'+'constraint_atoms.inp', 'r') as fcon:
          constraint_lines = [line for line in fcon if line.strip()]
      icon = 0
      countcon = len(constraint_lines)
    #f=(loop)
      for icon in range(0,countcon):
          connumero= open(macrotarget+'/'+'constraint_atoms.inp','r')
          consatom=connumero.readlines()
          connumero.close()
          consatom=str((consatom[icon]).strip('\n'))
          consatom=int(consatom)
          consatom=consatom+1
          consatom=str(consatom)
          yasara.run('FixAtom '+str(consatom))
          yasara.ShowMessage(str(consatom)+" atom will be fixed")
          icon=icon+1
      yasara.run('SelectRes con')
      yasara.run('FixAtom selected')
      yasara.ShowMessage("Geometry optimization is in progress..") 
    #yasara.run('UnselectAll')
    #yasara.run('MinStep 0.05')
      #yasara.ExperimentMinimization()
      #yasara.Experiment("On")
      #yasara.Wait("ExpEnd")
      #yasara.run('DelObj simcell')
      yasara.run('InflateObj all')
      yasara.run('DeflateAll')
      yasara.run('InflateAll')
      yasara.ShowMessage("Charge calculation is in progress..")
##Calculating the charge of the product
      #prochargeinfo=yasara.run('ChargeObj all')
      yasara.run('JoinObj all,1')
      yasara.run('SaveSMILES 1 ,'+macrotarget+'/'+str(nameobj)+'.smiles,transform=Yes')
      yasara.ShowMessage("Charge calculation is in process...")
      time.sleep(5)      
      smi=open(macrotarget+"/"+str(nameobj)+".smiles","r")
      smidata=smi.read()
      smi.close()
      mol=_require_molecule_from_smiles(smidata)
      prochargeinfo=Chem.GetFormalCharge(mol)
      promod=open(macrotarget+'/'+str(nameobj)+'procharge.log','w')
      promod.write(str(prochargeinfo).replace('Summed up net charge is ','').replace('[','').replace(']',''))
      promod.close()
      prochargef= open(macrotarget+'/'+str(nameobj)+'procharge.log','r')
      prochargeall=prochargef.readlines()
      prochargef.close()
      procharge=float((prochargeall[0]).strip('\n'))
      procharge=round(procharge)
      print(procharge)

      proalllist =\
        yasara.ShowWin("Custom","INFORMATION",400,250,
        "NumberInput", 20, 88,"Charge",str(procharge),-1000,1000,
        "NumberInput", 180, 88,"Multiplicity",1,1,1000,
        "Button",      150,200," O K")  
##counting the object present in the yasara window
      pcharge=open(macrotarget+'/'+str(nameobj)+'procharge.log','w+')
      pcharge.write((str(proalllist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
      pcharge.close()
      if os.path.getsize(macrotarget+'/'+str(nameobj)+'procharge.log') == 0:
        yasara.ShowMessage("Charge calculation failed, restart the process") 
        _safe_remove(macrotarget+'/'+str(nameobj)+'procharge.log')
        yasara.plugin.end() 
      else:
        print('ok')   

      pro_charge = open(macrotarget+'/'+str(nameobj)+'procharge.log', "r")
      productinfo= pro_charge.readlines()
      pro_charge.close()
      productcharge= str((productinfo[0]).strip('\n'))    
      productmultiplicity= str((productinfo[1]).strip('\n')) 


  ##counting the atom of product present in the yasara window
      proatom=yasara.run("Countatom all")
      prodeltext= open(macrotarget+'/'+'prodeltext.txt','w')
      prodeltext.write(str(proatom).replace('atom(s) match the selection.','').replace('[','').replace(']',''))
      prodeltext.close()
      p = open((macrotarget)+'/'+'prodeltext.txt', "r")
      pcontent = p.readlines()
      nopro=str((pcontent[0]).strip('\n').strip('[').strip(']'))
      p.close()
      atom=str(atom)
      _safe_remove((macrotarget)+'/'+'prodeltext.txt')
##checking the number of atom in product and reactant are same or not

      if nopro == atom :
      #yasara.run('JoinObj all,1')
        j=0
        nopro=int(nopro)
        for j in range (0,nopro):
            bfactor=yasara.run("BFactorAtom "+str(j+1))
            if j == 0:
              val= open(macrotarget+'/'+'product_bfactor.txt','w')
              val.write(str(bfactor).replace('[','').replace(']','').replace('.0',''))
              val.close()
            else:
              valread=open(macrotarget+'/'+'product_bfactor.txt','r')
              value=valread.readlines()
              valread.close()
              rewrite=open(macrotarget+'/'+'product_bfactor.txt','w')
              rewrite.writelines(value)
              rewrite.write('\n')
              rewrite.write(str(bfactor).replace('[','').replace(']','').replace('.0',''))
              rewrite.close()
        
            j=j+1 
      else:
       yasara.ShowMessage("WARNING! please see the terminal")
       print(nopro)
       print(atom)
       print("No. of atoms must be same for reactant and product")
       yasara.plugin.end()        


##Saving the xyz file of the product
      yasara.run("SaveXYZ all,"+str(macrotarget)+'/'+"QM_product.xyz,transform=Yes") 
      time.sleep(5)
##modifying the reactant.xyz file without hamparing the main file
      with open(str(macrotarget)+'/'+'QM_product.xyz', 'r') as fin:
          data = fin.read().splitlines(True)
      with open(str(macrotarget)+'/'+'QM_product.txt', 'w') as fout:
          fout.writelines(data[2:]) 
          fout.close()
   
##concatination of reactant xyz info with its b-factor value   
      procombine =[]

      with open((macrotarget)+'/'+'QM_product.txt') as xh:
        with open((macrotarget)+'/'+'product_bfactor.txt') as yh:
          with open((macrotarget)+'/'+'QM_product_filter.txt',"w") as zh:
       #Read first file
             xlines = xh.readlines()
         #Read second file
             ylines = yh.readlines()
         #Combine content of both lists
         #combine = list(zip(ylines,xlines))
         #Write to third file
             for i in range(len(xlines)):
                line = ylines[i].strip('\n') + '    ' + xlines[i]
                zh.write(line)

      yasara.run("clear")
      yasara.run("DelObj all")
      yasara.run('Loadxyz '+macrotarget+'/'+'QM.xyz')
      yasara.run('BallStickObj all')
      yasara.run('Loadxyz '+macrotarget+'/'+'QM_product.xyz')
      yasara.run('BallStickObj all')
      radius=yasara.run('RadiusObj 1')
      rd=open(macrotarget+'/'+'radius.txt','w+')
      rd.write(str(radius).replace('[','').replace(']','').replace('Object  1 (reactant) has a VdW radius of ','').replace('A from its geometric center',''))
      rd.close()
      fk=open(macrotarget+'/'+'radius.txt','r')
      r=fk.readline()
      fk.close()
      r=str(r)
      r=float(r)
      display_offset = 15
      y = r + display_offset
      y=str(y)
      z = -r - display_offset
      z=str(z)
#yasara.run('r=RadiusObj 1')
#yasara.run('len=15')
      yasara.run('MoveObj !1,X='+str(y))
      yasara.run('MoveObj 1,X='+str(z))
      yasara.run('ShowArrow Start=Point,X=-15,Y=0,Z=50,End=Point,X=15,Y=0,Z=50,Radius=1,Color=Yellow')
      yasara.run('ZoomAll Steps=0')
      yasara.run('Move Z=20')
      yasara.run('LabelObj 1,reactant,Color=Yellow,Y=5,Z=-5')
      yasara.run('LabelObj 2,product,Color=Yellow,Y=5,Z=-5')

      def sortLinesByColumn(readable, column, columnt_type):
          """Returns a list of strings (lines in readable file) in sorted order (based on column)"""
          lines = []

          for line in readable:
            # get the element in column based on which the lines are to be sorted
              column_element= columnt_type(line.split(' ')[column-1])
              lines.append((column_element, line))

          lines.sort()

          return [x[1] for x in lines]


      with open((macrotarget)+'/'+'QM_product_filter.txt') as f:
        # sort the lines based on column 1, and column 1 is type int
          sorted_lines = sortLinesByColumn(f, 1, int)
          k= open((macrotarget)+'/'+'QM_product_final.txt',"w")
          k.writelines(sorted_lines)
          k.close()

  #_safe_remove((macrotarget)+'/'+'product_filter.txt')
      proedit = open((macrotarget)+'/'+'QM_product_final.txt', "r")
      editfile = open((macrotarget)+'/'+'QM_product_filter.txt', "w")
      for line in proedit:
          if line.strip():
              editfile.write("\t".join(line.split()[1:]) + "\n")    
      proedit.close()
      editfile.close()
      _safe_remove((macrotarget)+'/'+'QM_product_final.txt')


      qmorcaproinp=open((macrotarget)+'/'+'QM_product_filter.txt')
      qmprodata=qmorcaproinp.read()
      qmorcaproinp.close()
      print(prodata)
      orca_geo_pro=open((macrotarget)+'/'+'QM_product.inp','w+')
      orca_geo_pro.write("!")
      orca_geo_pro.write(str(functional))
      orca_geo_pro.write(" ")
      orca_geo_pro.write(str(basis))
      orca_geo_pro.write(' Opt')
    #orca_geo_pro.write("\n%pal\n   nprocs ")
    #orca_geo_pro.write(str(processor))
    #orca_geo_pro.write('\nend')
      orca_geo_pro.write('\n%maxcore 101376\n%geom \nConstraints\n')
      orca_geo_pro.write(str(condata))
      orca_geo_pro.write('\nend\nend\n*xyz ')
      orca_geo_pro.write(str(productcharge))
      orca_geo_pro.write(" ")
      orca_geo_pro.write(str(productmultiplicity))
      orca_geo_pro.write("\n")
  #orca_geo_pro.write(str(reactdata))
      orca_geo_pro.write(str(qmprodata))
      orca_geo_pro.write("\n*")
      orca_geo_pro.close()
  


      yasara.ShowMessage("Geometry optimization is in progress..")  
      if mod == str(1) or mod == str(2): 
        print('check')
        _run_legacy_command(orca+' QM_product.inp >QM_product.out')
      else:
        _run_legacy_command('orca QM_product.inp >QM_product.out')




      yasara.ShowMessage("Geometry optimization is complete")
      tsinp=open((macrotarget)+'/'+'ts.inp','w+')
      tsinp.write('!')
      tsinp.write(str(functional))
      tsinp.write(' ')
      tsinp.write(str(basis))
      tsinp.write(' NEB-TS ')#FREQ')
    #tsinp.write("\n\n%pal\n   nprocs ")
    #tsinp.write(str(processor))
    #tsinp.write('\nend')
      tsinp.write('\n\n%neb\n\nNEB_End_XYZFile "QM_product.xyz"\n\nNImages ')
      tsinp.write(str(numeroimg))
      tsinp.write('\n\nend\n%geom \nConstraints\n')
      tsinp.write(str(condata))
      tsinp.write('\nend\nend\n*xyzfile ')
      tsinp.write(str(reactcharge))
      tsinp.write(' ')
      tsinp.write(str(reactmultiplicity))
      tsinp.write(' QM_reactant.xyz\n\n')
      tsinp.close()
      yasara.ShowMessage("Transition state calculation is in process..")
      os.chdir(pathYasara)
      os.chdir(macrotarget)
      time.sleep(5)
      if mod == str(1)or mod == str(2): 
        print('check')
        _run_legacy_command(orca+' ts.inp >ts.out')
      else:
        _run_legacy_command('orca ts.inp >ts.out')

    if os.path.isfile(macrotarget+'/'+'ts_MEP_trj.xyz') :
      trjlist =\
        yasara.ShowWin("Custom","Trjectory view",400,250,
         "Text", 20, 50, "Do you want to visualize trajectory?",
         "RadioButtons",2,1,
                        20, 100,"yes",
                        200,100,"no",
         "Button",      150,200," O K")
      attach= open((macrotarget)+'/'+'trjectory.txt','w+')
      attach.write((str(trjlist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
      attach.close()  
      f = open((macrotarget)+'/'+'trjectory.txt', "r")
      content= f.readlines()
      f.close()
      a = str((content[0]).strip('\n'))   
      if a == str(1):
        if mod == str(1):
          _safe_move(macrotarget+'/'+'ts_MEP_trj.xyz', macrotarget+'/'+'ts_MEP_final.xyz' )
        else:
           _safe_move(macrotarget+'/'+'ts_MEP_trj.xyz', macrotarget+'/'+'ts_MEP_final.xyz' )     
    
        yasara.run('DelObj all')  
        yasara.run('Loadxyz '+macrotarget+'/'+'ts_MEP_final.xyz')
        yasara.run('BallStickObj all')
        obj=yasara.run("CountObj all")
        deltext= open(macrotarget+'/'+'deltext.txt','w')
        deltext.write(str(obj).replace('object(s) match the selection.','').replace('[','').replace(']',''))
        deltext.close()
        g = open((macrotarget)+'/'+'deltext.txt', "r")
        content = g.readlines()
        noobj=str((content[0]).strip('\n'))
        g.close()
        noobj=int(noobj)
        k=0
        yasara.run('ZoomAll Steps=20')
        yasara.run('HideObj all')
        for k in range(0,noobj):
            yasara.run('ShowObj '+str(k+1))
            yasara.run('BallStickObj all')
            yasara.run("wait continuebutton")
            if int(k+1) == noobj :
              print('done')
            else:
              yasara.run('DelObj '+str(k+1))
            k=k+1
        yasara.ShowMessage("Transition state calculation is complete and results are saved in: "+ macrotarget)
  
      else:
        yasara.ShowMessage("Transition state calculation is complete and results are saved in: "+ macrotarget)    

    elif remethodology == str(1):
      nameobj = 'QM_reactant'
      try:
        homo, lumo, hlgap_eh, hlgap_ev = _save_homo_lumo_results(
          os.path.join(macrotarget, str(nameobj) + '.out'),
          os.path.join(macrotarget, str(nameobj))
        )
      except (OSError, ValueError) as error:
        yasara.ShowMessage(
          'The HOMO-LUMO analysis could not be completed.\n' + str(error)
        )
        yasara.plugin.end()
      else:
        yasara.ShowMessage(
          'HOMO orbital: ' + str(homo['number']) +
          '\nHOMO energy: ' + str(round(homo['energy_ev'], 4)) + ' eV' +
          '\n\nLUMO orbital: ' + str(lumo['number']) +
          '\nLUMO energy: ' + str(round(lumo['energy_ev'], 4)) + ' eV' +
          '\n\nHOMO-LUMO energy difference: ' + str(round(hlgap_ev, 2)) + ' eV'
        )
      yasara.plugin.end()

    elif remethodology == str(2):
      # PM3 and all other ORCA Fukui calculations use Mulliken charges.
      print('Fukui population scheme: Mulliken')
      atomcharge=int(reactcharge)
      reactmultiplicity=int(reactmultiplicity)
      newmultiplicity=reactmultiplicity+1
      newmultiplicity=str(newmultiplicity)
      #cation chrage
      cationcharge=(atomcharge+1)
      cationcharge=str(cationcharge)
      anioncharge=(atomcharge-1)
      anioncharge=str(anioncharge)
      print(cationcharge)
      print(anioncharge)
      print(newmultiplicity)
      with open(str(macrotarget)+'/'+'QM_reactant.xyz', 'r') as fin:
          data = fin.read().splitlines(True)
      with open(str(macrotarget)+'/'+'QM_reactant.txt', 'w') as fout:
          fout.writelines(data[2:]) 
          fout.close()  
      orcamolinp=open((macrotarget)+'/'+'QM_reactant.txt')
      moldata=orcamolinp.read()
      orcamolinp.close()
      k= open(macrotarget+'/'+'QM_reactant_cation.inp','w')
      k.write('! ')
      k.write(str(functional))
      k.write(' ')
      k.write(str(basis))
      k.write(' Opt Mulliken')
      k.write('\n%maxcore 101376\n%geom \nConstraints\n')
      k.write(str(condata))
      k.write('\nend\nend\n*xyz ')
      k.write(str(cationcharge))
      k.write(' ')
      k.write(str(newmultiplicity))
      k.write('\n')
      k.write(str(moldata))
      k.write('\n*')
      k.close()
      os.chdir(pathYasara)
      os.chdir(macrotarget)  
      yasara.ShowMessage("orca is optimizing cation")  
      if mod == str(1) or mod == str(2): 
        print('check')
        _run_legacy_command(orca+' QM_reactant_cation.inp >QM_reactant_cation.out')
      else:
        _run_legacy_command('orca QM_reactant_cation.inp >QM_reactant_cation.out')
      
      
      orca_anion=open((macrotarget)+'/'+'QM_reactant_anion.inp','w+')
      orca_anion.write("! ")
      orca_anion.write(str(functional))
      orca_anion.write(" ")
      orca_anion.write(str(basis))
      orca_anion.write(' OPT Mulliken')
      orca_anion.write('\n%maxcore 101376\n%geom \nConstraints\n')
      orca_anion.write(str(condata))
      orca_anion.write('\nend\nend\n*xyz ')
      orca_anion.write(str(anioncharge))
      orca_anion.write(" ")
      orca_anion.write(str(newmultiplicity))
      orca_anion.write("\n")
      orca_anion.write(str(moldata))
      orca_anion.write('\n*')
      orca_anion.close()
      yasara.ShowMessage("orca is optimizing anion")
      nameobj= 'QM_reactant'
      if mod == str(1) or mod == str(2):
        _run_legacy_command(orca+' '+macrotarget+'/'+str(nameobj)+'_anion.inp >  '+macrotarget+'/'+str(nameobj)+'_anion.out')
      else:
        _run_legacy_command('orca '+macrotarget+'/'+str(nameobj)+'_anion.inp >  '+macrotarget+'/'+str(nameobj)+'_anion.out')

      try:
        fukui_rows, fukui_results_path = _save_fukui_results(
          os.path.join(macrotarget, 'QM_reactant.out'),
          os.path.join(macrotarget, str(nameobj) + '_cation.out'),
          os.path.join(macrotarget, str(nameobj) + '_anion.out'),
          os.path.join(macrotarget, str(nameobj)),
          population_scheme='mulliken'
        )
      except (OSError, ValueError) as error:
        yasara.ShowMessage(
          'The Fukui-function analysis could not be completed.\n' + str(error)
        )
        yasara.plugin.end()
      else:
        yasara.ShowMessage(
          'Fukui function calculation is complete.\nResults: ' +
          fukui_results_path
        )
        yasara.run('saveYOB all,' + macrotarget + '/' + str(nameobj) + '.yob')
    else:
      #yasara.ShowMessage("check your structure")
      print('check your structure') 


    #else : 
      #yasara.ShowMessage("QM calculation failed. Please check output(.out) file for more information ") 
######## for single point calculation
elif method == 'ORCA' and methodology in {str(1), str(2), str(4), str(5), str(6), str(7), str(10), str(11)}:
  obj=yasara.run("CountObj all")
  deltext= open(macrotarget+'/'+'deltext.txt','w')
  deltext.write(str(obj).replace('object(s) match the selection.','').replace('[','').replace(']',''))
  deltext.close()
  g = open((macrotarget)+'/'+'deltext.txt', "r")
  content = g.readlines()
  noobj=str((content[0]).strip('\n'))
  g.close()


  if noobj== str(0):
    
    yasara.ShowMessage("Please build your molecule and then click continue")
    yasara.run("wait continuebutton")
    # reobj=yasara.run("CountObj all")
    # redeltext= open(macrotarget+'/'+'redeltext.txt','w')
    # redeltext.write(str(reobj).replace('object(s) match the selection.','').replace('[','').replace(']',''))
    # redeltext.close()
    # reg = open((macrotarget)+'/'+'redeltext.txt', "r")
    # recontent = reg.readlines()
    # renoobj=str((recontent[0]).strip('\n'))
    # reg.close()
    # if renoobj== 0 :
      # yasara.ShowMessage("QM calculation will be failed. Please load a structure")
      # _safe_remove(macrotarget+'/'+'redeltext.txt')
      # yasara.run("wait continuebutton")
    # else:
      # print('ok')
 
    #yasara.run('ForceField AMBER03,SetPar=Yes')
  ###charge of the  molecule
    #chargeinfo=yasara.run('ChargeObj all')
    yasara.run('JoinObj all,1')
    yasara.run('SaveSMILES 1 ,'+macrotarget+'/'+str(nameobj)+'.smiles,transform=Yes')
    yasara.ShowMessage("Charge calculation is in process...")
    time.sleep(5)    
    smi=open(macrotarget+"/"+str(nameobj)+".smiles","r")
    smidata=smi.read()
    smi.close()
    mol=_require_molecule_from_smiles(smidata)
    chargeinfo=Chem.GetFormalCharge(mol)
    yasara.run("SaveXYZ all,"+str(macrotarget)+'/'+str(nameobj)+".xyz,transform=Yes")
    cmod=open(macrotarget+'/'+str(nameobj)+'charge.log','w')
    cmod.write(str(chargeinfo).replace('Summed up net charge is ','').replace('[','').replace(']',''))
    cmod.close()
    if os.path.getsize(macrotarget+'/'+str(nameobj)+'charge.log')== 0:
      yasara.ShowMessage("QM calculation will be failed. Please load a structure")
      _safe_remove(macrotarget+'/'+'redeltext.txt')
      yasara.run("wait continuebutton")
      #yasara.run('ForceField AMBER03,SetPar=Yes')
  ###charge of the  molecule
      #chargeinfo=yasara.run('ChargeObj all')
      yasara.run('JoinObj all,1')
      yasara.run('SaveSMILES 1 ,'+macrotarget+'/'+str(nameobj)+'.smiles,transform=Yes')
      yasara.ShowMessage("Charge calculation is in process...")
      time.sleep(5)      
      smi=open(macrotarget+"/"+str(nameobj)+".smiles","r")
      smidata=smi.read()
      smi.close()
      mol=_require_molecule_from_smiles(smidata)
      prochargeinfo=Chem.GetFormalCharge(mol)      
      yasara.run("SaveXYZ all,"+str(macrotarget)+'/'+str(nameobj)+".xyz,transform=Yes")
      cmod=open(macrotarget+'/'+str(nameobj)+'charge.log','w')
      cmod.write(str(chargeinfo).replace('Summed up net charge is ','').replace('[','').replace(']',''))
      cmod.close()
    else:
      print('ok')  
    chargef= open(macrotarget+'/'+str(nameobj)+'charge.log','r')
    chargeall=chargef.readlines()
    chargef.close()
    charge=float((chargeall[0]).strip('\n'))
    charge=round(charge)
    print(charge)
####################################tempo section

        
####temposection

    
  else:
    yasara.ShowMessage("Please select your molecule by selectbox or join object all and then select all atoms")
    yasara.run("wait continuebutton")
    counts=yasara.run('CountAtom selected')
    countselect= open(macrotarget+'/'+'checkselect.txt','w')
    countselect.write(str(counts).replace('object(s) match the selection.','').replace('[','').replace(']','').replace("'",""))
    countselect.close()
    ck=os.path.getsize(macrotarget+'/'+'checkselect.txt')
    print(ck)
    if ck== 1:
       yasara.ShowMessage("Make sure that you have selected the object")
       yasara.run("wait continuebutton")      
    else:
       print('OK')

    nome=yasara.run('NameObj selected') 
    redeltext= open(macrotarget+'/'+'nome.txt','w')
    redeltext.write(str(nome).replace('object(s) match the selection.','').replace('[','').replace(']','').replace("'","").replace(', ','_'))
    redeltext.close()
    reg = open((macrotarget)+'/'+'nome.txt', "r")
    recontent = reg.readlines()
    nome=str((recontent[0]).strip('\n'))
    reg.close()
    print(nome)
    nameobj=str(nameobj)+"_"+str(nome)
    yasara.run("SaveSce "+str(macrotarget)+'/'+str(nameobj)+"_ini.sce")
    yasara.run('NumberObj selected,1')
    yasara.run('JoinObj all,1')
    yasara.run('Delatom all and not selected')
    #chargeinfo=yasara.run('ChargeObj all')
    #yasara.run('JoinObj all,1')
    yasara.run('SaveSMI all ,'+macrotarget+'/'+str(nameobj))
    os.chdir(plgpath)
    os.chdir(macrotarget)
    x=os.listdir(macrotarget)
    print(x)
    yasara.ShowMessage("Charge calculation is in process...")
    time.sleep(5)
    x=os.listdir(macrotarget)
    print(x)    
    with open(nameobj+".smi","r") as smi:
      smidata=smi.read()
    mol=_require_molecule_from_smiles(smidata)
    chargeinfo=Chem.GetFormalCharge(mol)    
    yasara.run("SaveSce "+str(macrotarget)+'/'+str(nameobj)+"_select.sce")
    yasara.run("SaveXYZ Selected,"+str(macrotarget)+'/'+str(nameobj)+".xyz,transform=Yes")
    yasara.run("SaveXYZ Selected,"+str(macrotarget)+'/'+str(nameobj)+"_ini.xyz,transform=Yes")
    #yasara.run('Clear')
    #yasara.run('Loadxyz '+(macrotarget)+'/'+str(nameobj)+'.xyz')
    #yasara.run('JoinObj all,1')
    #yasara.run("SaveXYZ Selected,"+str(macrotarget)+'/'+str(nameobj)+".xyz,transform=Yes")

    yasara.run('Clear')
    yasara.run('LoadSce '+str(macrotarget)+'/'+str(nameobj)+'_ini.sce,Settings=No')    
    
    
    #yasara.ShowMessage("Please select your molecule by selectbox or join object all and then select all atoms")
    #yasara.run("wait continuebutton")
    #yasara.run('ForceField AMBER03,SetPar=Yes')
  ###charge of the  molecule
    
   # yasara.run("SaveXYZ Selected,"+str(macrotarget)+'/'+str(nameobj)+".xyz,transform=Yes")
    cmod=open(macrotarget+'/'+str(nameobj)+'charge.log','w')
    cmod.write(str(chargeinfo).replace('Summed up net charge is ','').replace('[','').replace(']',''))
    cmod.close()
    if os.path.getsize(macrotarget+'/'+str(nameobj)+'charge.log')== 0:
      yasara.ShowMessage("QM calculation  will be failed. Please select a structure.")
      #_safe_remove(macrotarget+'/'+'redeltext.txt')
      yasara.run("wait continuebutton")
      nome=yasara.run('NameObj selected')
      print('ok')    
      redeltext= open(macrotarget+'/'+'nome.txt','w')
      redeltext.write(str(nome).replace('object(s) match the selection.','').replace('[','').replace(']','').replace("'","").replace(', ','_'))
      redeltext.close()
      reg = open((macrotarget)+'/'+'nome.txt', "r")
      recontent = reg.readlines()
      nome=str((recontent[0]).strip('\n'))
      reg.close()
      print(nome)
      nameobj=str(nameobj)+"_"+str(nome)    
      yasara.run("SaveSce "+str(macrotarget)+'/'+str(nameobj)+"_ini.sce")
      yasara.run('NumberObj selected,1')
      yasara.run('JoinObj all,1')
      yasara.run('Delatom all and not selected')
      #chargeinfo=yasara.run('ChargeObj all')
      yasara.run('JoinObj all,1')
      yasara.run('SaveSMILES 1 ,'+macrotarget+'/'+str(nameobj)+'.smiles,transform=Yes')
      yasara.ShowMessage("Charge calculation is in process...")
      time.sleep(5)      
      smi=open(macrotarget+"/"+str(nameobj)+".smiles","r")
      smidata=smi.read()
      smi.close()
      mol=_require_molecule_from_smiles(smidata)
      chargeinfo=Chem.GetFormalCharge(mol)      
      yasara.run("SaveSce "+str(macrotarget)+'/'+str(nameobj)+"_select.sce")
      yasara.run("SaveXYZ Selected,"+str(macrotarget)+'/'+str(nameobj)+".xyz,transform=Yes")
      yasara.run("SaveXYZ Selected,"+str(macrotarget)+'/'+str(nameobj)+"_ini.xyz,transform=Yes")

      yasara.run('Clear')
      yasara.run('LoadSce '+str(macrotarget)+'/'+str(nameobj)+'_ini.sce,Settings=No')    
    
    
    #yasara.ShowMessage("Please select your molecule by selectbox or join object all and then select all atoms")
    #yasara.run("wait continuebutton")
      #yasara.run('ForceField AMBER03,SetPar=Yes')
  ###charge of the  molecule
      cmod=open(macrotarget+'/'+str(nameobj)+'charge.log','w')
      cmod.write(str(chargeinfo).replace('Summed up net charge is ','').replace('[','').replace(']',''))
      cmod.close()
     
    chargef= open(macrotarget+'/'+str(nameobj)+'charge.log','r')
    chargeall=chargef.readlines()
    chargef.close()
    charge=float((chargeall[0]).strip('\n'))
    charge=round(charge)
    print(charge)    
  
  alllist =\
    yasara.ShowWin("Custom","INFORMATION",400,250,
    "NumberInput", 20, 88,"Charge",str(charge),-1000,1000,
    "NumberInput", 180, 88,"Multiplicity",1,1,1000,
    "Button",      150,200," O K")  
##counting the object present in the yasara window
  charge=open(macrotarget+'/'+str(nameobj)+'charge.log','w+')
  charge.write((str(alllist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
  charge.close()
  if os.path.getsize(macrotarget+'/'+str(nameobj)+'charge.log') == 0:
    yasara.ShowMessage("Charge calculation failed, restart the process") 
    _safe_remove(macrotarget+'/'+str(nameobj)+'charge.log')
    yasara.plugin.end() 
  else:
    print('ok')   

  react_charge = open(macrotarget+'/'+str(nameobj)+'charge.log', "r")
  reactinfo= react_charge.readlines()
  react_charge.close()
  reactcharge= str((reactinfo[0]).strip('\n'))    
  reactmultiplicity= str((reactinfo[1]).strip('\n'))
##modifying the reactant.xyz file without hamparing the main file
  with open(str(macrotarget)+'/'+str(nameobj)+'.xyz', 'r') as fin:
      data = fin.read().splitlines(True)
  with open(str(macrotarget)+'/'+str(nameobj)+'.txt', 'w') as fout:
      fout.writelines(data[2:])

  # Load the molecular coordinate block once for every ORCA methodology.
  # Previously this variable was created only inside selected calculation
  # branches, which caused direct NMR calculations to fail with NameError.
  molecular_coordinate_file = os.path.join(
      macrotarget,
      str(nameobj) + '.txt'
  )

  if not os.path.isfile(molecular_coordinate_file):
    yasara.ShowMessage(
        'The molecular coordinate file was not created:\n' +
        molecular_coordinate_file
    )
    yasara.plugin.end()

  with open(
      molecular_coordinate_file,
      'r',
      encoding='utf-8',
      errors='replace'
  ) as molecular_coordinate_handle:
    moldata = molecular_coordinate_handle.read()

  if not moldata.strip():
    yasara.ShowMessage(
        'The molecular coordinate block is empty. '
        'Please load or build a valid molecule and restart the calculation.'
    )
    yasara.plugin.end()

##for methodology single point charge and homo-lumo difference calculation
  if methodology == str(1) or  methodology ==str(6):
    orcamolinp=open((macrotarget)+'/'+str(nameobj)+'.txt')
    moldata=orcamolinp.read()
    orcamolinp.close()
    orca_sp=open((macrotarget)+'/'+str(nameobj)+'.inp','w+')
    orca_sp.write("! SP ")
    orca_sp.write(str(functional))
    orca_sp.write(" ")
    orca_sp.write(str(basis))
    orca_sp.write(" ")
   # orca_sp.write("\n%pal\n   nprocs ")
    #orca_sp.write(str(processor))
   # orca_sp.write('\nend')
    orca_sp.write("\n\n%maxcore 20480\n\n* xyz  ")
    orca_sp.write(str(reactcharge))
    orca_sp.write(" ")
    orca_sp.write(str(reactmultiplicity))
    orca_sp.write("\n")
    orca_sp.write(str(moldata))
    orca_sp.write('\n*')
    orca_sp.close()
    yasara.ShowMessage("orca is optimizing single point energies")
    if mod == str(1) or mod == str(2):
      _run_legacy_command(orca+' '+macrotarget+'/'+str(nameobj)+'.inp >  '+macrotarget+'/'+str(nameobj)+'.out')
    else:
      
      _run_legacy_command('orca '+macrotarget+'/'+str(nameobj)+'.inp >  '+macrotarget+'/'+str(nameobj)+'.out')
      
    #yasara.ShowMessage("Single point energy calculation is complete and results are saved in: "+ macrotarget)
    if os.path.isfile ((macrotarget+'/'+str(nameobj)+'.property.txt')):
      yasara.ShowMessage("Single point energy calculation is complete and results are saved in: "+ macrotarget)
      
    else:
      yasara.ShowMessage("Single point energy calculation is complete and results are saved in: "+ macrotarget)#yasara.ShowMessage("Single point energy calculation failed") 
      #yasara.plugin.end()
    if methodology == str(1):
      output_path = os.path.join(macrotarget, str(nameobj) + '.out')
      try:
        final_scf_energy = _extract_final_scf_energy(output_path)
      except (OSError, ValueError) as error:
        yasara.ShowMessage(
          'The single-point calculation finished, but its final energy '
          'could not be parsed.\n' + str(error)
        )
      else:
        yasara.ShowMessage(
          'Final single-point energy: ' +
          str(round(final_scf_energy, 10)) + ' Eh'
        )

        xyz_path = os.path.join(macrotarget, str(nameobj) + '.xyz')
        with open(xyz_path, 'r', encoding='utf-8', errors='replace') as xyz_handle:
          xyz_lines = xyz_handle.readlines()

        if len(xyz_lines) >= 2:
          final_structure_path = os.path.join(
            macrotarget,
            str(nameobj) + '_finalstructure.xyz'
          )
          second_line = xyz_lines[1].rstrip('\n')
          with open(final_structure_path, 'w', encoding='utf-8') as final_handle:
            final_handle.write(xyz_lines[0].rstrip('\n') + '\n')
            final_handle.write(
              second_line + ' SCF_ENERGY=' +
              str(final_scf_energy) + '\n'
            )
            final_handle.writelines(xyz_lines[2:])
    else:
      print('Parsing HOMO-LUMO energies')
      try:
        homo, lumo, hlgap_eh, hlgap_ev = _save_homo_lumo_results(
          os.path.join(macrotarget, str(nameobj) + '.out'),
          os.path.join(macrotarget, str(nameobj))
        )
      except (OSError, ValueError) as error:
        yasara.ShowMessage(
          'ORCA calculation finished, but the orbital energies could not be parsed.\n' +
          str(error)
        )
        yasara.plugin.end()
      else:
        yasara.ShowMessage(
          'HOMO orbital: ' + str(homo['number']) +
          '\nHOMO energy: ' + str(round(homo['energy_ev'], 4)) + ' eV' +
          '\n\nLUMO orbital: ' + str(lumo['number']) +
          '\nLUMO energy: ' + str(round(lumo['energy_ev'], 4)) + ' eV' +
          '\n\nHOMO-LUMO energy difference: ' + str(round(hlgap_ev, 2)) + ' eV'
        )
##for methodology geometry optimization
  elif methodology == str(2) or methodology == str(10):  
    orcamolinp=open((macrotarget)+'/'+str(nameobj)+'.txt')
    moldata=orcamolinp.read()
    orcamolinp.close()
    orca_geo=open((macrotarget)+'/'+str(nameobj)+'.inp','w+')
    orca_geo.write("! ")
    orca_geo.write(str(functional))
    orca_geo.write(" ")
    orca_geo.write(str(basis))
    orca_geo.write(" ")
    orca_geo.write('OPT')
    if methodology == str(10):
      orca_geo.write(' Mulliken')
    #orca_geo.write("\n%pal\n   nprocs ")
    #orca_geo.write(str(processor))
    #orca_geo.write('\nend')
    orca_geo.write("\n\n* xyz  ")
    orca_geo.write(str(reactcharge))
    orca_geo.write(" ")
    orca_geo.write(str(reactmultiplicity))
    orca_geo.write("\n")
    orca_geo.write(str(moldata))
    orca_geo.write('\n*')
    orca_geo.close()
    yasara.ShowMessage("orca is optimizing the geometry")
    
    if mod == str(1) or mod == str(2):
      _run_legacy_command(orca+' '+macrotarget+'/'+str(nameobj)+'.inp >  '+macrotarget+'/'+str(nameobj)+'.out')
    else:
      _run_legacy_command('orca '+macrotarget+'/'+str(nameobj)+'.inp >  '+macrotarget+'/'+str(nameobj)+'.out')
    
    yasara.run('Clear')
    yasara.run('Loadxyz '+macrotarget+'/'+str(nameobj)+'.xyz')
    yasara.ShowMessage("Geometry optimization is complete and results are saved in: "+ macrotarget)
##########fukui function calculation####
    if methodology == str(10):
      #yasara.run("Delobj all and not selected")
      atomcharge=int(reactcharge)
      reactmultiplicity=int(reactmultiplicity)
      newmultiplicity=reactmultiplicity+1
      newmultiplicity=str(newmultiplicity)
      #cation chrage
      cationcharge=(atomcharge+1)
      cationcharge=str(cationcharge)
      anioncharge=(atomcharge-1)
      anioncharge=str(anioncharge)
      print(cationcharge)
      print(anioncharge)
      print(newmultiplicity)

##geometry optimixation of cation
      orca_cat=open((macrotarget)+'/'+str(nameobj)+'_cation.inp','w+')
      orca_cat.write("! ")
      orca_cat.write(str(functional))
      orca_cat.write("  ")
      orca_cat.write(str(basis))
      orca_cat.write(' OPT Mulliken')
      orca_cat.write("\n\n* xyz  ")
      orca_cat.write(str(cationcharge))
      orca_cat.write(" ")
      orca_cat.write(str(newmultiplicity))
      orca_cat.write("\n")
      orca_cat.write(str(moldata))
      orca_cat.write('\n*')
      orca_cat.close()
      yasara.ShowMessage("orca is optimizing cation")
    
      if mod == str(1) or mod == str(2):
        _run_legacy_command(orca+' '+macrotarget+'/'+str(nameobj)+'_cation.inp >  '+macrotarget+'/'+str(nameobj)+'_cation.out')
      else:
        _run_legacy_command('orca '+macrotarget+'/'+str(nameobj)+'_cation.inp >  '+macrotarget+'/'+str(nameobj)+'_cation.out')

##geometry optimixation of anion
      orca_anion=open((macrotarget)+'/'+str(nameobj)+'_anion.inp','w+')
      orca_anion.write("! ")
      orca_anion.write(str(functional))
      orca_anion.write(" ")
      orca_anion.write(str(basis))
      orca_anion.write(' OPT Mulliken')
      orca_anion.write("\n\n* xyz  ")
      orca_anion.write(str(anioncharge))
      orca_anion.write(" ")
      orca_anion.write(str(newmultiplicity))
      orca_anion.write("\n")
      orca_anion.write(str(moldata))
      orca_anion.write('\n*')
      orca_anion.close()
      yasara.ShowMessage("orca is optimizing anion")
    
      if mod == str(1) or mod == str(2):
        _run_legacy_command(orca+' '+macrotarget+'/'+str(nameobj)+'_anion.inp >  '+macrotarget+'/'+str(nameobj)+'_anion.out')
      else:
        _run_legacy_command('orca '+macrotarget+'/'+str(nameobj)+'_anion.inp >  '+macrotarget+'/'+str(nameobj)+'_anion.out')

      try:
        fukui_rows, fukui_results_path = _save_fukui_results(
          os.path.join(macrotarget, str(nameobj) + '.out'),
          os.path.join(macrotarget, str(nameobj) + '_cation.out'),
          os.path.join(macrotarget, str(nameobj) + '_anion.out'),
          os.path.join(macrotarget, str(nameobj)),
          population_scheme='mulliken'
        )
      except (OSError, ValueError) as error:
        yasara.ShowMessage(
          'The Fukui-function analysis could not be completed.\n' + str(error)
        )
        yasara.plugin.end()
      else:
        yasara.ShowMessage(
          'Fukui function calculation is complete.\nResults: ' +
          fukui_results_path
        )
        yasara.run('saveYOB all,' + macrotarget + '/' + str(nameobj) + '.yob')

    else:
      #yasara.ShowMessage("check your structure")
      print('check your structure')
  
###for methodology of user's choice
  elif methodology == str(7):  
    orcamolinp=open((macrotarget)+'/'+str(nameobj)+'.txt')
    moldata=orcamolinp.read()
    orcamolinp.close()
    orca_geo=open((macrotarget)+'/'+str(nameobj)+'.inp','w+')
    orca_geo.write("! ")
    orca_geo.write(str(functional))
    orca_geo.write(" ")
    orca_geo.write(str(basis))
    #orca_geo.write("\n%pal\n   nprocs ")
   # orca_geo.write(str(processor))
    #orca_geo.write('\nend')
    orca_geo.write("\n\n* xyz  ")
    orca_geo.write(str(reactcharge))
    orca_geo.write(" ")
    orca_geo.write(str(reactmultiplicity))
    orca_geo.write("\n")
    orca_geo.write(str(moldata))
    orca_geo.write('\n*')
    orca_geo.close()
    yasara.ShowMessage("orca is optimizing the molecule")
    
    if mod == str(1) or mod == str(2):     
     _run_legacy_command(orca+' '+macrotarget+'/'+str(nameobj)+'.inp >  '+macrotarget+'/'+str(nameobj)+'.out')
      
    else:
      _run_legacy_command('orca '+macrotarget+'/'+str(nameobj)+'.inp >  '+macrotarget+'/'+str(nameobj)+'.out')
    
    yasara.ShowMessage("ORCA calculation is complete and results are saved in: "+ macrotarget)


##for meethodology vibrational frequency
  elif methodology == str(4):  
    orcamolinp=open((macrotarget)+'/'+str(nameobj)+'.txt')
    moldata=orcamolinp.read()
    orcamolinp.close()
    orca_geo=open((macrotarget)+'/'+str(nameobj)+'.inp','w+')
    orca_geo.write("! ")
    orca_geo.write(str(functional))
    orca_geo.write(" ")
    orca_geo.write(str(basis))
    orca_geo.write(" ")
    orca_geo.write('OPT FREQ')
    #orca_geo.write("\n%pal\n   nprocs ")
    #orca_geo.write(str(processor))
    #orca_geo.write('\nend')
    orca_geo.write("\n\n* xyz  ")
    orca_geo.write(str(reactcharge))
    orca_geo.write(" ")
    orca_geo.write(str(reactmultiplicity))
    orca_geo.write("\n")
    orca_geo.write(str(moldata))
    orca_geo.write('\n*')
    orca_geo.close()
    yasara.ShowMessage("orca is optimizing the Vibrational frequencies")
    if mod == str(1) or mod == str(2):
      _run_legacy_command(orca+' '+macrotarget+'/'+str(nameobj)+'.inp >  '+macrotarget+'/'+str(nameobj)+'.out')
      
    else: 
      _run_legacy_command('orca '+macrotarget+'/'+str(nameobj)+'.inp >  '+macrotarget+'/'+str(nameobj)+'.out')
    
    if os.path.isfile(macrotarget+'/'+str(nameobj)+'.hess'):
      yasara.ShowMessage("Vibrational frequencies optimization is complete and results are saved in: "+ macrotarget)
      trjlist =\
        yasara.ShowWin("Custom","Trjectory view",400,250,
         "Text", 20, 50, "Do you want to visualize trajectory?",
         "RadioButtons",2,1,
                        20, 100,"yes",
                        200,100,"no",
         "Button",      150,200," O K")
      attach= open((macrotarget)+'/'+str(nameobj)+'_trjectory.txt','w+')
      attach.write((str(trjlist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
      attach.close()  
      f = open((macrotarget)+'/'+str(nameobj)+'_trjectory.txt', "r")
      content= f.readlines()
      f.close()
      a = str((content[0]).strip('\n'))   
      if a == str(1):
        if mod == str(1):
          _safe_move(macrotarget+'/'+str(nameobj)+'_trj.xyz', macrotarget+'/'+str(nameobj)+'_trajectory.xyz' )
        else:
          _safe_move(macrotarget+'/'+str(nameobj)+'_trj.xyz', macrotarget+'/'+str(nameobj)+'_trajectory.xyz' )
        yasara.run('DelObj all')  
        yasara.run('Loadxyz '+macrotarget+'/'+str(nameobj)+'_trajectory.xyz')
        yasara.run('ZoomAll Steps=20')
        obj=yasara.run("CountObj all")
        deltext= open(macrotarget+'/'+'deltext.txt','w')
        deltext.write(str(obj).replace('object(s) match the selection.','').replace('[','').replace(']',''))
        deltext.close()
        g = open((macrotarget)+'/'+'deltext.txt', "r")
        content = g.readlines()
        noobj=str((content[0]).strip('\n'))
        g.close()
        noobj=int(noobj)
        k=0
      
        yasara.run('HideObj all')
        for k in range(0,noobj):
            yasara.run('ZoomAll Steps=20')
            yasara.run('ShowObj '+str(k+1))
          #time.sleep(1)
            if int(k+1) == noobj :
              print('done')
            else:
              yasara.run('DelObj '+str(k+1))
            k=k+1

    else:
      yasara.ShowMessage("Vibrational frequencies calculation failed with error")
      print('please see the inputmolecule.out file for more information')


  elif methodology == str(11):
    unsupported_nmr_methods = {'XTB', 'RHF PM3', 'MP2', 'CCSD'}
    if str(functional).strip().upper() in {value.upper() for value in unsupported_nmr_methods}:
      yasara.ShowMessage(
        'The selected method does not provide the combined shielding and '
        'J-coupling workflow used here. Select HF or a DFT functional.'
      )
      yasara.plugin.end()
    if not str(basis).strip() or str(basis).strip().lower() == 'none':
      yasara.ShowMessage(
        'NMR calculation requires an explicit basis set. '
        'pcSseg-1/pcSseg-2 or a sufficiently flexible def2 basis is recommended.'
      )
      yasara.plugin.end()

    nmr_options = yasara.ShowWin(
      "Custom", "ORCA NMR OPTIONS", 600, 400,
      "Text", 20, 50, "NMR spectrum parameters",
      "NumberInput", 20, 75, "Spectrometer frequency (MHz)", 400, 1, 2000,
      "NumberInput", 20, 130, "1H reference shielding (ppm)", 31.77, -10000, 10000,
      "NumberInput", 20, 185, "13C reference shielding (ppm)", 188.10, -10000, 10000,
      "NumberInput", 20, 240, "J-coupling distance threshold (A)", 5, 1, 100,
      "Button", 542, 348, " O K"
    )
    nmr_option_values = _numeric_dialog_values(nmr_options)
    nmr_frequency = nmr_option_values[0] if len(nmr_option_values) > 0 else 400.0
    nmr_h_reference = nmr_option_values[1] if len(nmr_option_values) > 1 else 31.77
    nmr_c_reference = nmr_option_values[2] if len(nmr_option_values) > 2 else 188.10
    nmr_distance_threshold = nmr_option_values[3] if len(nmr_option_values) > 3 else 5.0

    if nmr_frequency <= 0:
      yasara.ShowMessage('The NMR spectrometer frequency must be greater than zero.')
      yasara.plugin.end()
    if nmr_distance_threshold <= 0:
      yasara.ShowMessage('The J-coupling distance threshold must be greater than zero.')
      yasara.plugin.end()


    nmr_base = os.path.join(macrotarget, str(nameobj) + '_nmr')
    nmr_input = nmr_base + '.inp'
    nmr_output = nmr_base + '.out'
    nmr_elements = {
      line.split()[0].capitalize()
      for line in str(moldata).splitlines()
      if len(line.split()) >= 4
    }
    nmr_nuclei_lines = []
    if 'H' in nmr_elements:
      nmr_nuclei_lines.append('  Nuclei = all H {shift, ssall, ist=1}')
    if 'C' in nmr_elements:
      nmr_nuclei_lines.append('  Nuclei = all C {shift, ssall, ist=13}')
    if not nmr_nuclei_lines:
      yasara.ShowMessage('The ORCA NMR workflow currently requires at least one H or C atom.')
      yasara.plugin.end()

    with open(nmr_input, 'w', encoding='utf-8') as nmr_handle:
      nmr_handle.write('! ' + str(functional) + ' ' + str(basis) + ' OPT TightSCF NMR KeepDens\n')
      nmr_handle.write('\n* xyz ' + str(reactcharge) + ' ' + str(reactmultiplicity) + '\n')
      nmr_handle.write(str(moldata))
      if not str(moldata).endswith('\n'):
        nmr_handle.write('\n')
      nmr_handle.write('*\n\n%eprnmr\n')
      nmr_handle.write('\n'.join(nmr_nuclei_lines) + '\n')
      nmr_handle.write('  SpinSpinRThresh ' + str(nmr_distance_threshold) + '\n')
      nmr_handle.write('end\n')

    yasara.ShowMessage('ORCA geometry optimization and NMR calculation are in progress.')
    nmr_return_code = _run_orca(nmr_input, nmr_output)
    if nmr_return_code != 0 or not os.path.isfile(nmr_output):
      yasara.ShowMessage('ORCA NMR calculation failed. Please inspect ' + nmr_output)
      yasara.plugin.end()

    try:
      nmr_shieldings = _parse_nmr_shieldings(nmr_output)
      nmr_j_labels, nmr_j_matrix = _parse_j_coupling_matrix(nmr_output)
    except Exception as nmr_parse_error:
      yasara.ShowMessage('NMR output parsing failed: ' + str(nmr_parse_error))
      yasara.plugin.end()

    if not nmr_shieldings:
      yasara.ShowMessage(
        'ORCA completed, but no isotropic NMR shieldings were found in the output.'
      )
      yasara.plugin.end()
    if not nmr_j_matrix:
      print(
        'WARNING: No isotropic J-coupling matrix was parsed. '
        'The fallback spectrum will contain unsplit lines.'
      )

    nmr_shielding_csv = nmr_base + '_shieldings.csv'
    with open(nmr_shielding_csv, 'w', encoding='utf-8', newline='') as handle:
      writer = csv.writer(handle)
      writer.writerow(['Atom', 'Element', 'Isotropic_shielding_ppm', 'Chemical_shift_ppm'])
      for shielding in nmr_shieldings:
        atomic_number = _ATOMIC_NUMBERS.get(shielding['element'].upper())
        reference = {1: nmr_h_reference, 6: nmr_c_reference}.get(atomic_number)
        chemical_shift = reference - shielding['shielding_ppm'] if reference is not None else ''
        writer.writerow([
          shielding['index'] + 1,
          shielding['element'],
          shielding['shielding_ppm'],
          chemical_shift
        ])

    nmr_j_csv = nmr_base + '_J_coupling_matrix.csv'
    _write_j_coupling_csv(nmr_j_csv, nmr_j_labels, nmr_j_matrix)

    nmr_spec_input = nmr_base + '.nmrspec'
    nmr_spec_output = nmr_base + '_spectrum.out'
    nmr_basename = os.path.basename(nmr_base)
    with open(nmr_spec_input, 'w', encoding='utf-8') as handle:
      handle.write('NMRShieldingFile = "' + nmr_basename + '"\n')
      handle.write('NMRCouplingFile = "' + nmr_basename + '"\n')
      handle.write('NMRSpecFreq = ' + str(nmr_frequency) + '\n')
      handle.write('PrintLevel = 0\n')
      handle.write('NMRCoal = 1.0\n')
      if 'H' in nmr_elements:
        handle.write('NMRREF[1] ' + str(nmr_h_reference) + '\n')
      if 'C' in nmr_elements:
        handle.write('NMRREF[6] ' + str(nmr_c_reference) + '\n')
      handle.write('END\n')

    nmr_spectrum_executable_name = 'orca_nmrspectrum.exe' if mod == str(2) else 'orca_nmrspectrum'
    nmr_spectrum_executable = os.path.join(orcap, nmr_spectrum_executable_name)
    nmr_peaks = {}
    used_orca_nmrspectrum = False
    if os.path.isfile(nmr_spectrum_executable) and os.path.isfile(nmr_base + '.gbw'):
      nmr_spectrum_return_code = _run_executable(
        nmr_spectrum_executable,
        [os.path.basename(nmr_base + '.gbw'), os.path.basename(nmr_spec_input)],
        workdir=macrotarget,
        stdout_path=nmr_spec_output,
        show_error=False
      )
      if nmr_spectrum_return_code == 0 and os.path.isfile(nmr_spec_output):
        nmr_peaks = _parse_nmrspectrum_peaks(nmr_spec_output)
        used_orca_nmrspectrum = bool(nmr_peaks)

    if not nmr_peaks:
      print('WARNING: orca_nmrspectrum did not produce readable peaks; using first-order J splitting.')
      nmr_peaks = _simulate_first_order_nmr(
        nmr_shieldings,
        nmr_j_labels,
        nmr_j_matrix,
        nmr_frequency,
        {1: nmr_h_reference, 6: nmr_c_reference}
      )

    nmr_peak_csv = nmr_base + '_peaks.csv'
    _write_nmr_peak_csv(nmr_peak_csv, nmr_peaks)
    nmr_images = _create_nmr_plots(nmr_peaks, nmr_base, nmr_frequency)

    try:
      nmr_energy = _extract_final_scf_energy(nmr_output)
    except Exception:
      nmr_energy = None
    nmr_details = {
      'Engine': 'ORCA',
      'Calculation': 'Optimized NMR shielding and spin-spin coupling',
      'Functional': functional,
      'Basis': basis,
      'Charge': reactcharge,
      'Multiplicity': reactmultiplicity,
      'Spectrometer frequency (MHz)': nmr_frequency,
      '1H reference shielding (ppm)': nmr_h_reference,
      '13C reference shielding (ppm)': nmr_c_reference,
      'J-coupling distance threshold (A)': nmr_distance_threshold,
      'Final electronic energy (Eh)': format(nmr_energy, '.12f') if nmr_energy is not None else None,
      'NMR simulation': 'ORCA spin-Hamiltonian diagonalization' if used_orca_nmrspectrum else 'First-order J-matrix fallback'
    }
    nmr_xyz = _find_structure_file(nmr_base, input_path=nmr_input)
    nmr_homo_cube = nmr_base + '_HOMO.cube' if os.path.isfile(nmr_base + '_HOMO.cube') else None
    nmr_lumo_cube = nmr_base + '_LUMO.cube' if os.path.isfile(nmr_base + '_LUMO.cube') else None
    nmr_report = _generate_html_report(
      nmr_base,
      'ORCA',
      nmr_details,
      xyz_path=nmr_xyz,
      homo_cube=nmr_homo_cube,
      lumo_cube=nmr_lumo_cube,
      image_paths=nmr_images,
      data_files=[
        nmr_input,
        nmr_output,
        nmr_base + '.property.txt',
        nmr_spec_input,
        nmr_spec_output,
        nmr_shielding_csv,
        nmr_j_csv,
        nmr_peak_csv,
        nmr_homo_cube,
        nmr_lumo_cube
      ],
      nmr_peaks=nmr_peaks,
      j_labels=nmr_j_labels,
      j_matrix=nmr_j_matrix
    )

    if nmr_images:
      yasara.run('LoadPNG ' + nmr_images[0])
      yasara.run('ShowImage 1,Alpha=100,Priority=0')
    yasara.ShowMessage(
      'NMR calculation and J-coupled spectrum are complete.\n'
      'Interactive report: ' + nmr_report
    )

###for methodology uv spectroscopy
  else:
    if mod == str(1) or mod == str(2):
      if mod == str(1):
        src = os.path.join(orcap, 'orca_mapspc')
        dst = os.path.join(macrotarget, 'orca_mapspc')
      else:
        src = os.path.join(orcap, 'orca_mapspc.exe')
        dst = os.path.join(macrotarget, 'orca_mapspc.exe')
      if not os.path.isfile(src):
        yasara.ShowMessage(
          'The ORCA spectrum utility was not found:\n' + src
        )
        yasara.plugin.end()
      try:
        shutil.copy2(src, dst)
      except shutil.SameFileError:
        pass
      except OSError as copy_error:
        yasara.ShowMessage(
          'Could not prepare orca_mapspc for UV-Vis processing:\n' +
          str(copy_error)
        )
        yasara.plugin.end()
    else:
      print('ORCA mapspc utility preparation skipped.')
    resultlist =\
      yasara.ShowWin("Custom","SOLVENT SELECTION",600,400,
      "List",        20,70,"Solvent",250,250,"No",                 
                     15,   "None(gas)",
                           "Water",
                           "Acetonitrile",
                           "Acetone",
                           "Ethanol",
                           "Methanol",
                           "CCl4",
                           "CH2Cl2",
                           "Chloroform",
                           "DMSO",
                           "DMF",
                           "Hexane",
                           "Toluene",
                           "Pyridine",
                           "THF",
      "Button",      542,348," O K")


    solv= open((macrotarget)+'/'+'solvent.txt', 'w+')
    solv.write((str(resultlist)).replace("'","").replace(" ", "\n").replace("[1","").replace("]","").replace(",",""))
    solv.write('\n')
    solv.close()    
    f = open((macrotarget)+'/'+'solvent.txt', "r")
    content= f.readlines()
    f.close()
    solvent= str((content[1]).strip('\n'))
    print(content)
    print(solvent)
    if solvent == "None":
      solvent= ' '
    else:
      solvent = 'CPCM('+str(solvent)+')'
 
    print(solvent)
    
    orcamolinp=open((macrotarget)+'/'+str(nameobj)+'.txt')
    moldata=orcamolinp.read()
    orcamolinp.close()
    orca_uv=open((macrotarget)+'/'+str(nameobj)+'.inp','w+')
    orca_uv.write("! ")
    orca_uv.write(str(functional))
    orca_uv.write(" ")
    orca_uv.write(str(basis))
    orca_uv.write(" ")
    orca_uv.write(str(solvent))
    #orca_uv.write("\n%pal\n   nprocs ")
    #orca_uv.write(str(processor))
    #orca_uv.write('\nend')
    orca_uv.write("\n\n%TDDFT\n\n   NROOTS   40\n\nEND\n\n*xyz  ")
    orca_uv.write(str(reactcharge))
    orca_uv.write(" ")
    orca_uv.write(str(reactmultiplicity))
    orca_uv.write("\n")
    orca_uv.write(str(moldata))
    orca_uv.write('\n*')
    #orca_uv.write("inputmolecule.xyz")
    orca_uv.close()
    #orca_geo.write("\n")
    #orca_geo.write(str(moldata))
    #orca_geo.write('\n*')
    #orca_geo.close()
    #_safe_remove((macrotarget)+'/'+'solvent.txt')
    yasara.ShowMessage("orca is calculating the UV-Vis spectroscopy")
    if mod == str(1) or mod == str(2):
      _run_legacy_command(orca+' '+macrotarget+'/'+str(nameobj)+'.inp >  '+macrotarget+'/'+str(nameobj)+'.out')  
      yasara.ShowMessage("done") 
      os.chdir(macrotarget)
      if mod == str(1):
        _run_legacy_command('./orca_mapspc '+macrotarget+'/'+str(nameobj)+'.out ABS -W1000' )
      else:
        _run_legacy_command('orca_mapspc.exe '+macrotarget+'/'+str(nameobj)+'.out ABS -W1000' )      
    else:
      _run_legacy_command('orca '+macrotarget+'/'+str(nameobj)+'.inp >  '+macrotarget+'/'+str(nameobj)+'.out')  
      yasara.ShowMessage("done") 
      os.chdir(macrotarget)
      _run_legacy_command('orca_mapspc '+macrotarget+'/'+str(nameobj)+'.out ABS -W1000' )      
    print('++++++')
    
    file_path = macrotarget+'/'+str(nameobj)+'.out.abs.dat'
    dataframe1 = pd.read_csv(file_path, sep=r'\s+')

    dataframe1.to_csv((macrotarget)+'/'+str(nameobj)+'.csv', index = None)
    df = pd.read_csv((macrotarget)+'/'+str(nameobj)+'.csv', header=None)
    df.rename(columns={0: 'name', 1: 'id'}, inplace=True)
    df.to_csv((macrotarget)+'/'+'uvdata.csv', index=False)
    hr= pd.read_csv((macrotarget)+'/'+'uvdata.csv')
    hr=pd.DataFrame(hr)
    hr['wavelength'] = ((1/hr['name']*10000000).round(0))
    dr=pd.DataFrame(hr)
    dr.to_csv((macrotarget)+'/'+str(nameobj)+'_uvdata.csv', index = None)




    with open((macrotarget)+'/'+str(nameobj)+'_uvdata.csv', 'r+') as f:
      headers = f.readline()
      firstData = f.readline()
      f.seek(0)
      firstData = firstData[:-1] + ' ' * len(headers) + '\n'
      f.write(firstData)
    with open((macrotarget)+'/'+str(nameobj)+'_uvdata.csv', 'r+') as fd:
        lines = fd.readlines()
        fd.seek(0)
        fd.writelines(line for line in lines if line.strip())
        fd.truncate()
    
    x = []
    y = []
    
    with open((macrotarget)+'/'+str(nameobj)+'_uvdata.csv','r') as csvfile:
        plots = csv.reader(csvfile, delimiter = ',')
      
        for row in plots:
            x.append(float(row[5]))
            y.append(float(row[1]))
  
    plt.plot(x, y, color = 'red', linestyle = 'dashed')
    plt.xlim(150,800)
    plt.ylim(-1)
    plt.xlabel('Wavelength(nm)')
    plt.ylabel('Absorbance')
    plt.title('UV-Vis Spectroscopy analysis')
#plt.grid()
    plt.savefig((macrotarget)+'/'+str(nameobj)+'_uvdata.png')
    plt.close()     
    thirdpng='LoadPNG '+(macrotarget)+'/'+str(nameobj)+'_uvdata.png'
    yasara.run(thirdpng)
    yasara.run("ShowImage 1,Alpha=100,Priority=0")

    uv_base = os.path.join(macrotarget, str(nameobj))
    uv_details = {
      'Engine': 'ORCA',
      'Calculation': 'TD-DFT UV-Vis spectrum',
      'Functional': functional,
      'Basis': basis,
      'Solvent model': solvent if str(solvent).strip() else 'Gas phase',
      'Charge': reactcharge,
      'Multiplicity': reactmultiplicity
    }
    try:
      uv_details['Final electronic energy (Eh)'] = format(
        _extract_final_scf_energy(uv_base + '.out'),
        '.12f'
      )
    except Exception:
      pass
    uv_report = _generate_html_report(
      uv_base,
      'ORCA',
      uv_details,
      xyz_path=_find_structure_file(uv_base, input_path=uv_base + '.inp'),
      homo_cube=uv_base + '_HOMO.cube' if os.path.isfile(uv_base + '_HOMO.cube') else None,
      lumo_cube=uv_base + '_LUMO.cube' if os.path.isfile(uv_base + '_LUMO.cube') else None,
      image_paths=[uv_base + '_uvdata.png'],
      data_files=[
        uv_base + '.inp',
        uv_base + '.out',
        uv_base + '.property.txt',
        uv_base + '.out.abs.dat',
        uv_base + '_uvdata.csv',
        uv_base + '_uvdata.png',
        uv_base + '_HOMO.cube',
        uv_base + '_LUMO.cube'
      ]
    )
    yasara.ShowMessage(
      "UV-Vis spectroscopy analysis is complete.\nInteractive report: " + uv_report
    )

else :
  print("++++")

########### MOPAC calculation
#### MOPAC INPUT FILE FORMATION ###################################################################################################
if method == 'MOPAC' : 
###object selection  
  obj=yasara.run("CountObj all")
  deltext= open(macrotarget+'/'+'deltext.txt','w')
  deltext.write(str(obj).replace('object(s) match the selection.','').replace('[','').replace(']',''))
  deltext.close()
  g = open((macrotarget)+'/'+'deltext.txt', "r")
  content = g.readlines()
  noobj=str((content[0]).strip('\n'))
  g.close()
  if noobj== str(0):
    if methodology == 'Import-job' and os.path.isfile(macrotarget+'/'+ownfile):
      print("ownfile is present") 
    else:
      yasara.ShowMessage("Please build your molecule and then click continue")
      yasara.run("wait continuebutton") 
      reobj=yasara.run("CountObj all")
      redeltext= open(macrotarget+'/'+'redeltext.txt','w')
      redeltext.write(str(reobj).replace('object(s) match the selection.','').replace('[','').replace(']',''))
      redeltext.close()
      reg = open((macrotarget)+'/'+'redeltext.txt', "r")
      recontent = reg.readlines()
      renoobj=str((recontent[0]).strip('\n'))
      reg.close()
      if renoobj == str(0):
        yasara.ShowMessage("QM calculation failed. Please load a structure and restart the process")
        _safe_remove(macrotarget+'/'+'redeltext.txt')
        yasara.plugin.end()
      yasara.run('joinObj all,1')
      yasara.run("SaveXYZ 1,"+str(macrotarget)+'/'+str(nameobj)+".xyz,transform=Yes")
      yasara.run('DelObj all')  
      yasara.run('Loadxyz '+(macrotarget)+'/'+str(nameobj)+'.xyz')
    ###charge and multiplicity calculation
      #yasara.run('ForceField AMBER03,SetPar=Yes')
###charge of the reactant molecule
      #chargeinfo=yasara.run('ChargeObj all')
      yasara.run('JoinObj all,1')
      yasara.run('SaveSMILES 1 ,'+macrotarget+'/'+str(nameobj)+'.smiles,transform=Yes')
      yasara.ShowMessage("Charge calculation is in process...")
      time.sleep(5)      
      smi=open(macrotarget+"/"+str(nameobj)+".smiles","r")
      smidata=smi.read()
      smi.close()
      mol=_require_molecule_from_smiles(smidata)
      chargeinfo=Chem.GetFormalCharge(mol)      
      cfmod=open(macrotarget+'/'+str(nameobj)+'charge.log','w')
      cfmod.write(str(chargeinfo).replace('Summed up net charge is ','').replace('[','').replace(']','').replace(',','\n'))
      cfmod.close()
      chargef= open(macrotarget+'/'+str(nameobj)+'charge.log','r')
      chargeall=chargef.readlines()
      chargef.close()
      charge=float((chargeall[0]).strip('\n'))
      charge=round(charge)
      print(charge)
      alllist =\
        yasara.ShowWin("Custom","INFORMATION",400,250,
        "NumberInput", 20, 88,"Charge",str(charge),-1000,1000,
        "NumberInput", 180, 88,"Multiplicity",1,1,6,
        "Button",      150,200," O K")  
  ##counting the object present in the yasara window
      rcharge=open(macrotarget+'/'+str(nameobj)+'charge.log','w+')
      rcharge.write((str(alllist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
      rcharge.close()
      if os.path.getsize(macrotarget+'/'+str(nameobj)+'charge.log') == 0:
        yasara.ShowMessage("Charge calculation failed, restart the process") 
        _safe_remove(macrotarget+'/'+str(nameobj)+'charge.log')
        yasara.plugin.end() 
      else:
        print('ok')   

      react_charge = open(macrotarget+'/'+str(nameobj)+'charge.log', "r")
      reactinfo= react_charge.readlines()
      react_charge.close()
      reactcharge= str((reactinfo[0]).strip('\n'))    
      reactmultiplicity= str((reactinfo[1]).strip('\n')) 
      if reactmultiplicity == str(1):
        reactmultiplicity= 'SINGLET'
      elif reactmultiplicity == str(2):
        reactmultiplicity= 'DOUBLET'
      elif reactmultiplicity == str(3):
        reactmultiplicity= 'TRIPLET'
      elif reactmultiplicity == str(4):
        reactmultiplicity= 'QUARTET'
      elif reactmultiplicity == str(5):
        reactmultiplicity= 'QUINTET'
      else:
        reactmultiplicity= 'SEXTET'

  else:    
    
    yasara.ShowMessage("Please select your molecule by selectbox or join object all and then select all atoms")
    yasara.run("wait continuebutton")
    counts=yasara.run('CountAtom selected')
    countselect= open(macrotarget+'/'+'checkselect.txt','w')
    countselect.write(str(counts).replace('object(s) match the selection.','').replace('[','').replace(']','').replace("'",""))
    countselect.close()
    ck=os.path.getsize(macrotarget+'/'+'checkselect.txt')
    print(ck)
    if ck== 1:
       yasara.ShowMessage("Make sure that you have selected the object")
       yasara.run("wait continuebutton")      
    else:
       print('OK')
    nome=yasara.run('NameObj selected')
    print('ok')    
    redeltext= open(macrotarget+'/'+'nome.txt','w')
    redeltext.write(str(nome).replace('object(s) match the selection.','').replace('[','').replace(']','').replace("'","").replace(', ','_'))
    redeltext.close()
    reg = open((macrotarget)+'/'+'nome.txt', "r")
    recontent = reg.readlines()
    nome=str((recontent[0]).strip('\n'))
    reg.close()
    print(nome)
    nameobj=str(nameobj)+"_"+str(nome)
    yasara.run("SaveSce "+str(macrotarget)+'/'+str(nameobj)+"_ini.sce")
    yasara.run('NumberObj selected,1')
    yasara.run('JoinObj all,1')
    yasara.run('Delatom all and not selected')
    yasara.run("SaveSce "+str(macrotarget)+'/'+str(nameobj)+"_select.sce")
    yasara.run("SaveXYZ Selected,"+str(macrotarget)+'/'+str(nameobj)+".xyz,transform=Yes")
    #yasara.run('Clear')
    #yasara.run('Loadxyz '+(macrotarget)+'/'+str(nameobj)+'.xyz')
    #yasara.run('JoinObj all,1')
    #yasara.run("SaveXYZ Selected,"+str(macrotarget)+'/'+str(nameobj)+".xyz,transform=Yes")

    yasara.run('Clear')
    yasara.run('LoadSce '+str(macrotarget)+'/'+str(nameobj)+'_ini.sce,Settings=No')
    
    #yasara.run('DelObj all and not selected')
    #yasara.run('RemoveObj all and not selected')
    #yasara.run('DelObj all')  
    #yasara.run('Loadxyz '+(macrotarget)+'/'+str(nameobj)+'.xyz')
    ###charge and multiplicity calculation
    #yasara.run('ForceField AMBER03,SetPar=Yes')
###charge of the reactant molecule
    #chargeinfo=yasara.run('ChargeObj selected')
    yasara.run('JoinObj all,1')
    yasara.run('SaveSMILES 1 ,'+macrotarget+'/'+str(nameobj)+'.smiles,transform=Yes')
    yasara.ShowMessage("Charge calculation is in process...")
    time.sleep(5)    
    smi=open(macrotarget+"/"+str(nameobj)+".smiles","r")
    smidata=smi.read()
    smi.close()
    mol=_require_molecule_from_smiles(smidata)
    chargeinfo=Chem.GetFormalCharge(mol)    
    cfmod=open(macrotarget+'/'+str(nameobj)+'charge.log','w')
    cfmod.write(str(chargeinfo).replace('Summed up net charge is ','').replace('[','').replace(']','').replace(',','\n'))
    cfmod.close()
    if os.path.getsize(macrotarget+'/'+str(nameobj)+'charge.log')== 0:
      yasara.ShowMessage("QM calculation  will be failed. Please select a structure.")
      #_safe_remove(macrotarget+'/'+'redeltext.txt')
      yasara.run("wait continuebutton")
      nome=yasara.run('NameObj selected')
      print('ok')    
      redeltext= open(macrotarget+'/'+'nome.txt','w')
      redeltext.write(str(nome).replace('object(s) match the selection.','').replace('[','').replace(']','').replace("'","").replace(', ','_'))
      redeltext.close()
      reg = open((macrotarget)+'/'+'nome.txt', "r")
      recontent = reg.readlines()
      nome=str((recontent[0]).strip('\n'))
      reg.close()
      print(nome)
      nameobj=str(nameobj)+"_"+str(nome)
      yasara.run("SaveSce "+str(macrotarget)+'/'+str(nameobj)+"_ini.sce")
      yasara.run('NumberObj selected,1')
      yasara.run('JoinObj all,1')
      yasara.run('Delatom all and not selected')
      #chargeinfo=yasara.run('ChargeObj all')
      yasara.run('JoinObj all,1')
      yasara.run('SaveSMILES 1 ,'+macrotarget+'/'+str(nameobj)+'.smiles,transform=Yes')
      yasara.ShowMessage("Charge calculation is in process...")
      time.sleep(5)      
      smi=open(macrotarget+"/"+str(nameobj)+".smiles","r")
      smidata=smi.read()
      smi.close()
      mol=_require_molecule_from_smiles(smidata)
      chargeinfo=Chem.GetFormalCharge(mol)
      yasara.run("SaveSce "+str(macrotarget)+'/'+str(nameobj)+"_select.sce")
      yasara.run("SaveXYZ Selected,"+str(macrotarget)+'/'+str(nameobj)+".xyz,transform=Yes")
      yasara.run("SaveXYZ Selected,"+str(macrotarget)+'/'+str(nameobj)+"_ini.xyz,transform=Yes")

      yasara.run('Clear')
      yasara.run('LoadSce '+str(macrotarget)+'/'+str(nameobj)+'_ini.sce,Settings=No')    
    
    
    #yasara.ShowMessage("Please select your molecule by selectbox or join object all and then select all atoms")
    #yasara.run("wait continuebutton")
      #yasara.run('ForceField AMBER03,SetPar=Yes')
  ###charge of the  molecule
      cmod=open(macrotarget+'/'+str(nameobj)+'charge.log','w')
      cmod.write(str(chargeinfo).replace('Summed up net charge is ','').replace('[','').replace(']',''))
      cmod.close() 

    chargef= open(macrotarget+'/'+str(nameobj)+'charge.log','r')
    chargeall=chargef.readlines()
    chargef.close()
    charge=float((chargeall[0]).strip('\n'))
    charge=round(charge)
    print(charge)
    alllist =\
      yasara.ShowWin("Custom","INFORMATION",400,250,
      "NumberInput", 20, 88,"Charge",str(charge),-1000,1000,
      "NumberInput", 180, 88,"Multiplicity",1,1,6,
      "Button",      150,200," O K")  
##counting the object present in the yasara window
    rcharge=open(macrotarget+'/'+str(nameobj)+'charge.log','w+')
    rcharge.write((str(alllist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
    rcharge.close()
    if os.path.getsize(macrotarget+'/'+str(nameobj)+'charge.log') == 0:
      yasara.ShowMessage("Charge calculation failed, restart the process") 
      _safe_remove(macrotarget+'/'+str(nameobj)+'charge.log')
      yasara.plugin.end() 
    else:
      print('ok')   

    react_charge = open(macrotarget+'/'+str(nameobj)+'charge.log', "r")
    reactinfo= react_charge.readlines()
    react_charge.close()
    reactcharge= str((reactinfo[0]).strip('\n'))    
    reactmultiplicity= str((reactinfo[1]).strip('\n')) 
    if reactmultiplicity == str(1):
      reactmultiplicity= 'SINGLET'
    elif reactmultiplicity == str(2):
      reactmultiplicity= 'DOUBLET'
    elif reactmultiplicity == str(3):
      reactmultiplicity= 'TRIPLET'
    elif reactmultiplicity == str(4):
      reactmultiplicity= 'QUARTET'
    elif reactmultiplicity == str(5):
      reactmultiplicity= 'QUINTET'
    else:
      reactmultiplicity= 'SEXTET'


## MOPAC UV-Visible spectroscopy: optimize first, then vertical CI excitations
  if methodology == 'UV-Vis spectroscopy':
    if str(reactmultiplicity).upper() != 'SINGLET':
      yasara.ShowMessage(
        'The automated MOPAC UV-Visible workflow currently supports RHF singlet systems only.'
      )
      yasara.plugin.end()

    uv_options = yasara.ShowWin(
      "Custom", "MOPAC UV-VIS OPTIONS", 600, 400,
      "Text", 20, 50, "Excited-state model",
      "RadioButtons", 2, 1,
                      20, 65, "INDO/S (recommended)",
                      250, 65, "Selected PMx with MECI",
      "NumberInput", 20, 125, "C.I. active orbitals", 10, 2, 60,
      "NumberInput", 20, 180, "Minimum wavelength (nm)", 150, 1, 5000,
      "NumberInput", 20, 235, "Maximum wavelength (nm)", 800, 2, 10000,
      "NumberInput", 20, 290, "Gaussian FWHM (nm)", 15, 1, 500,
      "Button", 542, 348, " O K"
    )
    uv_values = _numeric_dialog_values(uv_options)
    uv_model_index = int(round(uv_values[0])) if len(uv_values) > 0 else 1
    uv_active_orbitals = int(round(uv_values[1])) if len(uv_values) > 1 else 10
    uv_minimum_wavelength = uv_values[2] if len(uv_values) > 2 else 150.0
    uv_maximum_wavelength = uv_values[3] if len(uv_values) > 3 else 800.0
    uv_fwhm = uv_values[4] if len(uv_values) > 4 else 15.0
    uv_excitation_model = 'INDO/S' if uv_model_index == 1 else 'PMx MECI'

    mopac_uv_prefix = os.path.join(macrotarget, str(nameobj))
    mopac_uv_xyz = os.path.join(macrotarget, str(nameobj) + '.xyz')
    try:
      mopac_uv_result = _run_mopac_uv_pipeline(
        mopac_uv_prefix,
        mopac_uv_xyz,
        theory,
        reactcharge,
        reactmultiplicity,
        uv_excitation_model,
        uv_active_orbitals,
        uv_minimum_wavelength,
        uv_maximum_wavelength,
        uv_fwhm
      )
    except Exception as mopac_uv_error:
      yasara.ShowMessage('MOPAC UV-Visible workflow failed:\n' + str(mopac_uv_error))
      yasara.plugin.end()

    if os.path.isfile(mopac_uv_result['optimized_xyz']):
      yasara.run('DelObj all')
      yasara.run('LoadXYZ ' + mopac_uv_result['optimized_xyz'])
    if os.path.isfile(mopac_uv_result['image']):
      yasara.run('LoadPNG ' + mopac_uv_result['image'])
      yasara.run('ShowImage 1,Alpha=100,Priority=0')
    yasara.ShowMessage(
      'MOPAC UV-Visible calculation is complete.\n' +
      'Transitions: ' + str(len(mopac_uv_result['transitions'])) + '\n' +
      'Interactive report: ' + mopac_uv_result['report']
    )
    yasara.plugin.end()

##homo-lumo energy gap calculation    
  if methodology == 'HOMO-LUMO':  
    if theory == ' ' :
      yasara.run('QuantumMechanics AM1')
      keys="DENSITY"
      yasara.run('LogAs '+(str(macrotarget))+'/'+str(nameobj)+'_qm_log,Append=No,RunMOPACObj 1,'+str(keys))    
      with open(macrotarget+'/'+str(nameobj)+'_qm_log.log',"r") as fin, open(macrotarget+'/'+str(nameobj)+'_qm_first.txt',"w") as fout:
           string = 'EIGENVALUES'
           for line in fin:
               if string in line:
                  fout.write(line)
                  try: 
                     while 'ATOMIC ORBITAL ELECTRON POPULATIONS' not in line:
                         line = next(fin)
                         fout.write(line)
                  except StopIteration:
                      pass  # ran out of file to read
                
      with open(macrotarget+'/'+str(nameobj)+'_qm_first.txt',"r") as fin, open(macrotarget+'/'+str(nameobj)+'_EIGENVALUES.txt',"w") as fout:
           string = 'EIGENVALUES'
           for line in fin:
               if string in line:
                  fout.write(line)
                  try: 
                     while 'NET ATOMIC CHARGES AND DIPOLE CONTRIBUTIONS' not in line:
                         line = next(fin)
                         fout.write(line)
                  except StopIteration:
                      pass  # ran out of file to read                
      remove_words=['NET']
      with open(macrotarget+'/'+str(nameobj)+'_EIGENVALUES.txt') as oldfile, open(macrotarget+'/'+str(nameobj)+'_EIGENVALUES_filter.txt', 'w') as newfile:
          for line in oldfile:
              if not any(remove_word in line for remove_word in remove_words):
                  newfile.write((line).replace('EIGENVALUES',''))

      _safe_remove(macrotarget+'/'+str(nameobj)+'_EIGENVALUES.txt')
      with open(macrotarget+'/'+str(nameobj)+'_EIGENVALUES_filter.txt') as reader, open(macrotarget+'/'+str(nameobj)+'_EIGENVALUES_filter.txt', 'r+') as writer:
        for line in reader:
          if line.strip():
            writer.write((line).replace('\n',''))
        writer.truncate()

      with open(macrotarget+'/'+str(nameobj)+'_qm_log.log',"r") as fin, open(macrotarget+'/'+str(nameobj)+'_qm_value.txt',"w") as fout:
           string = 'IONIZATION POTENTIAL'
           for line in fin:
               if string in line:
                  fout.write(line)
                  try: 
                     while 'NO. OF FILLED LEVELS' not in line:
                         line = next(fin)
                         fout.write(str(line).replace('IONIZATION POTENTIAL    =         ','').replace('NO. OF FILLED LEVELS    =         ',''))
                  except StopIteration:
                      pass  # ran out of file to read
      with open (macrotarget+'/'+str(nameobj)+'_qm_value.txt',"r") as f:
          data=f.readlines()
          p=((data[1]).strip('\n').strip('          '))
          print(p)
          f.close()
      p=int(p)
      m= p-1
      m=str(m)


      eigenarr = np.genfromtxt(macrotarget+'/'+str(nameobj)+'_EIGENVALUES_filter.txt')
      eigenarr=np.array(eigenarr)
  #eigenarr=np.array(eigenarr)
  #x=eigenarr[eigenarr < 0]
      a= eigenarr[int(p)]
      print(a)
      b= eigenarr[int(m)]
      print(b)
      a=float(a)
      b=float(b)
      energydiff=(a-b)
      homolumodiff= round(energydiff,3)
      lumo = round(a,3)
      homo = round(b,3)
      _safe_remove(macrotarget+'/'+str(nameobj)+'_EIGENVALUES_filter.txt')
      yasara.ShowMessage(" HOMO " + (str(homo)) + " LUMO " + (str(lumo)) + " gap: " + (str(homolumodiff))+ " eV")
    else:

      fh = open(macrotarget+'/'+str(nameobj)+'.xyz', "r")
      gh = open(macrotarget+'/'+str(nameobj)+'_xyz.txt', "w")
      for line in fh:
         if line.strip():
            gh.write("\t".join(line.split()[1:]) + "\n")

      fh.close()
      gh.close()
      x= open(macrotarget+'/'+str(nameobj)+'_xyz.txt','r')
      data=x.read()
      x.close()

      y=open(macrotarget+'/'+str(nameobj)+'_xyz.txt','w+')
      y.write(str(data).replace("	","0 0	").replace("\n","0 0\n"))
      y.close()
      fh = open(macrotarget+'/'+str(nameobj)+'.xyz', "r")
      gh = open(macrotarget+'/'+str(nameobj)+'_atomname.txt', "w")
      for line in fh:
         if line.strip():
            gh.write("\t".join(line.split()[:1]) + "\n")

      fh.close()
      gh.close()

      combine =[]

      with open(macrotarget+'/'+str(nameobj)+'_xyz.txt') as xh:
        with open(macrotarget+'/'+str(nameobj)+'_atomname.txt') as yh:
          with open(macrotarget+'/'+str(nameobj)+'.txt',"w") as zh:
             #Read first file
             xlines = xh.readlines()
               #Read second file
             ylines = yh.readlines()
               #Combine content of both lists
               #combine = list(zip(ylines,xlines))
               #Write to third file
             for i in range(len(xlines)):
                line = ylines[i].strip('\n') + '    ' + xlines[i]
                zh.write(line)
      os.chdir(plgpath)
      os.chdir(macrotarget)                    
      with open(macrotarget+'/'+str(nameobj)+'.txt', 'r') as fin:
         data = fin.read().splitlines(True)
      with open(macrotarget+'/'+str(nameobj)+'.txt', 'w') as fout:
         fout.writelines(data[1:])
         fout.close()
      f = open((macrotarget)+'/'+str(nameobj)+'.txt', "r")
      molcontent= f.read()
      f.close()
      if not firstkey or not secondkey or not thirdkey:
         yasara.ShowMessage(
            "MOPAC keywords were not initialized for " + str(methodology)
         )
         yasara.plugin.end()
      inp=open(macrotarget+'/'+str(nameobj)+'.mop', 'w+')
      inp.write(" ")
      inp.write(str(firstkey))
      inp.write(str(reactcharge)) 
      inp.write(" ")
      inp.write(str(reactmultiplicity))
      inp.write(" ")
      inp.write(str(secondkey))
      inp.write(" ")
      inp.write(str(theory))
      inp.write(" ")      
      inp.write(str(thirdkey))
      inp.write(" ")
      inp.write(str(hf))
      inp.write("\n\n\n")  
      inp.write(str(molcontent)) 
      inp.write("\n")    
      inp.close()
      print(mopac)
      with open(macrotarget+'/'+str(nameobj)+'.mop') as f, open(macrotarget+'/'+str(nameobj)+'_edit.mop', "w") as working:    
          for line in f:   
             if ".xyz" not in line:  
                 working.write(line)  
      _safe_remove(macrotarget+'/'+str(nameobj)+'.mop')  
      _safe_move(macrotarget+'/'+str(nameobj)+'_edit.mop', macrotarget+'/'+str(nameobj)+'.mop')       
      
      os.chdir(plgpath)
      os.chdir(macrotarget)      
      _run_legacy_command(mopac+' '+macrotarget+'/'+str(nameobj)+'.mop')
      energygapline= open(macrotarget+'/'+str(nameobj)+'.out')
      for line in energygapline:
          if "HOMO LUMO ENERGIES (EV) = " in line:
             print(line)
             line=str(line).strip("\n").strip("   ")
             ev=open(macrotarget+'/'+str(nameobj)+'_homo-lumo.txt', 'w+')
             ev.write((str(line)).replace('HOMO LUMO ENERGIES (EV) =        ','').replace(' ','\n'))
             ev.close()
             with open((macrotarget)+'/'+str(nameobj)+'_homo-lumo.txt', 'r+') as fd:
                 lines = fd.readlines()
                 fd.seek(0)
                 fd.writelines(line for line in lines if line.strip())
                 fd.truncate()             
             
             evgap=open(macrotarget+'/'+str(nameobj)+'_homo-lumo.txt')
             evgaplines=evgap.readlines()
             evgap.close()
             homo=(evgaplines[0]).strip('\n')
             lumo=(evgaplines[1]).strip('\n')

             homo=float(homo)
             lumo=float(lumo)
             energydiff=(lumo-homo)
             homolumodiff= round(energydiff,3)
             yasara.ShowMessage(" HOMO " + (str(homo)) + " LUMO " + (str(lumo)) + " gap: " + (str(homolumodiff))+ " eV")
             #yasara.ShowMessage(str(line))
             #_safe_remove(macrotarget+'/'+str(nameobj)+'_homo-lumo.txt')
             yasara.plugin.end()
      energygapline.close()


  elif methodology == 'Single-point': 

      fh = open(macrotarget+'/'+str(nameobj)+'.xyz', "r")
      gh = open(macrotarget+'/'+str(nameobj)+'_xyz.txt', "w")
      for line in fh:
         if line.strip():
            gh.write("\t".join(line.split()[1:]) + "\n")

      fh.close()
      gh.close()
      x= open(macrotarget+'/'+str(nameobj)+'_xyz.txt','r')
      data=x.read()
      x.close()

      y=open(macrotarget+'/'+str(nameobj)+'_xyz.txt','w+')
      y.write(str(data).replace("	","0 0	").replace("\n","0 0\n"))
      y.close()

      fh = open(macrotarget+'/'+str(nameobj)+'.xyz', "r")
      gh = open(macrotarget+'/'+'atomname.txt', "w")
      for line in fh:
         if line.strip():
            gh.write("\t".join(line.split()[:1]) + "\n")

      fh.close()
      gh.close()

      combine =[]

      with open(macrotarget+'/'+str(nameobj)+'_xyz.txt') as xh:
        with open(macrotarget+'/'+'atomname.txt') as yh:
          with open(macrotarget+'/'+str(nameobj)+'.txt',"w") as zh:
             #Read first file
             xlines = xh.readlines()
               #Read second file
             ylines = yh.readlines()
               #Combine content of both lists
               #combine = list(zip(ylines,xlines))
               #Write to third file
             for i in range(len(xlines)):
                line = ylines[i].strip('\n') + '    ' + xlines[i]
                zh.write(line)
      os.chdir(plgpath)
      os.chdir(macrotarget)                    
      with open(macrotarget+'/'+str(nameobj)+'.txt', 'r') as fin:
         data = fin.read().splitlines(True)
      with open(macrotarget+'/'+str(nameobj)+'.txt', 'w') as fout:
         fout.writelines(data[1:])
         fout.close()
      #with open(macrotarget+'/'+'inputmolecule.txt', 'r') as ffin:
         #fdata = ffin.read().splitlines(True)
      #with open(macrotarget+'/'+'datainputmolecule.txt', 'w') as ffout:
         #ffout.writelines(fdata[1:])
         #ffout.close()

      #yasara.run("wait continuebutton")
      #_safe_remove(macrotarget+'/'+str(nameobj)+'_xyz.txt')
      f = open((macrotarget)+'/'+str(nameobj)+'.txt', "r")
      molcontent= f.read()
      f.close()
      if not firstkey or not secondkey or not thirdkey:
         yasara.ShowMessage(
            "MOPAC keywords were not initialized for " + str(methodology)
         )
         yasara.plugin.end()
      inp=open(macrotarget+'/'+str(nameobj)+'.mop', 'w+')
      inp.write(" ")
      inp.write(str(firstkey))
      inp.write(str(reactcharge)) 
      inp.write(" ")
      inp.write(str(reactmultiplicity))
      inp.write(" ")
      inp.write(str(secondkey))
      inp.write(" ")
      inp.write(str(theory))
      inp.write(" ")      
      inp.write(str(thirdkey))
      inp.write(" ")
      inp.write(str(hf))
      inp.write("\n\n\n")  
      inp.write(str(molcontent)) 
      inp.write("\n")    
      inp.close()
      #print(mopac)
      with open(macrotarget+'/'+str(nameobj)+'.mop') as f, open(macrotarget+'/'+str(nameobj)+'_edit.mop', "w") as working:    
          for line in f:   
             if ".xyz" not in line:  
                 working.write(line)  
      _safe_remove(macrotarget+'/'+str(nameobj)+'.mop')  
      _safe_move(macrotarget+'/'+str(nameobj)+'_edit.mop', macrotarget+'/'+str(nameobj)+'.mop')       
      
      os.chdir(plgpath)
      os.chdir(macrotarget)

      mopac_input_path = os.path.join(
        macrotarget,
        str(nameobj) + '.mop'
      )
      mopac_output_path = os.path.join(
        macrotarget,
        str(nameobj) + '.out'
      )

      mopac_return_code = _run_legacy_command(
        str(mopac) + ' ' + mopac_input_path
      )

      if mopac_return_code != 0:
        yasara.ShowMessage(
          'MOPAC single-point calculation failed with return code ' +
          str(mopac_return_code) +
          '.\nPlease inspect:\n' +
          mopac_output_path
        )
        yasara.plugin.end()

      if not _mopac_output_has_results(mopac_output_path):
        yasara.ShowMessage(
          'MOPAC did not produce a usable single-point result.\n'
          'Please inspect the output file for SCF or keyword errors:\n' +
          mopac_output_path
        )
        yasara.plugin.end()

      mopac_energies = _parse_mopac_single_point_energies(
        mopac_output_path
      )

      if not mopac_energies:
        yasara.ShowMessage(
          'MOPAC completed, but the energy summary could not be parsed.\n'
          'Please inspect:\n' +
          mopac_output_path
        )
        yasara.plugin.end()

      if not _mopac_terminated_normally(mopac_output_path):
        print(
          'WARNING: MOPAC energy results were found, but the normal '
          'completion marker was not detected.'
        )

      mopac_pdb_path = os.path.join(
        macrotarget,
        str(nameobj) + '.pdb'
      )
      if os.path.isfile(mopac_pdb_path):
        yasara.run('DelObj all')
        yasara.run('Loadpdb ' + mopac_pdb_path)

      yasara.ShowMessage(
        _format_mopac_single_point_message(
          mopac_energies,
          mopac_output_path
        )
      )

  elif methodology == 'Equilibrium-geometry': 

      fh = open(macrotarget+'/'+str(nameobj)+'.xyz', "r")
      gh = open(macrotarget+'/'+str(nameobj)+'_xyz.txt', "w")
      for line in fh:
         if line.strip():
            gh.write("\t".join(line.split()[1:]) + "\n")

      fh.close()
      gh.close()
      x= open(macrotarget+'/'+str(nameobj)+'_xyz.txt','r')
      data=x.read()
      x.close()

      y=open(macrotarget+'/'+str(nameobj)+'_xyz.txt','w+')
      y.write(str(data).replace("	","1 1	").replace("\n","1 1\n"))
      y.close()

      fh = open(macrotarget+'/'+str(nameobj)+'.xyz', "r")
      gh = open(macrotarget+'/'+str(nameobj)+'_atomname.txt', "w")
      for line in fh:
         if line.strip():
            gh.write("\t".join(line.split()[:1]) + "\n")

      fh.close()
      gh.close()

      combine =[]

      with open(macrotarget+'/'+str(nameobj)+'_xyz.txt') as xh:
        with open(macrotarget+'/'+str(nameobj)+'_atomname.txt') as yh:
          with open(macrotarget+'/'+str(nameobj)+'.txt',"w") as zh:
             #Read first file
             xlines = xh.readlines()
               #Read second file
             ylines = yh.readlines()
               #Combine content of both lists
               #combine = list(zip(ylines,xlines))
               #Write to third file
             for i in range(len(xlines)):
                line = ylines[i].strip('\n') + '    ' + xlines[i]
                zh.write(line)
                   
      os.chdir(plgpath)
      os.chdir(macrotarget)                    
      with open(macrotarget+'/'+str(nameobj)+'.txt', 'r') as fin:
         data = fin.read().splitlines(True)
      with open(macrotarget+'/'+str(nameobj)+'_edit.txt', 'w') as fout:
         fout.writelines(data[1:])
         fout.close()
      #with open(macrotarget+'/'+'inputmolecule_edit.txt', 'r') as ffin:
         #fdata = ffin.read().splitlines(True)
      #with open(macrotarget+'/'+'datainputmolecule.txt', 'w') as ffout:
         #ffout.writelines(fdata[1:])
         #ffout.close()
      #_safe_remove(macrotarget+'/'+str(nameobj)+'_xyz.txt')
      f = open((macrotarget)+'/'+str(nameobj)+'_edit.txt', "r")
      molcontent= f.read()
      f.close()
      if not firstkey or not secondkey or not thirdkey:
         yasara.ShowMessage(
            "MOPAC keywords were not initialized for " + str(methodology)
         )
         yasara.plugin.end()
      inp=open(macrotarget+'/'+str(nameobj)+'.mop', 'w+')
      inp.write(" ")
      inp.write(str(firstkey))
      inp.write(str(reactcharge)) 
      inp.write(" ")
      inp.write(str(reactmultiplicity))
      inp.write(" ")
      inp.write(str(secondkey))
      inp.write(" ")
      inp.write(str(theory))
      inp.write(" ")      
      inp.write(str(thirdkey))
      inp.write(" ")
      inp.write(str(hf))
      inp.write("\n\n\n")  
      inp.write(str(molcontent)) 
      inp.write("\n")    
      inp.close()
      print(mopac)
      with open(macrotarget+'/'+str(nameobj)+'.mop') as f, open(macrotarget+'/'+str(nameobj)+'_edit.mop', "w") as working:    
          for line in f:   
             if ".xyz" not in line:  
                 working.write(line)  
      _safe_remove(macrotarget+'/'+str(nameobj)+'.mop')  
      _safe_move(macrotarget+'/'+str(nameobj)+'_edit.mop', macrotarget+'/'+str(nameobj)+'.mop') 

      os.chdir(plgpath)
      os.chdir(macrotarget)
      _run_legacy_command(mopac+' '+macrotarget+'/'+str(nameobj)+'.mop')
      if os.path.isfile(macrotarget+'/'+str(nameobj)+'.pdb'):
         yasara.ShowMessage('Geometry equilibration is complete and results are saved in :'+str(macrotarget))   
         yasara.run('DelObj all')
         yasara.run('LoadPDB '+macrotarget+'/'+str(nameobj)+'.pdb')
         #_safe_move(macrotarget+'/'+str(nameobj)+'.xyz',macrotarget+'/'+'output.xyz') 
         yasara.plugin.end()
      else:
         yasara.ShowMessage('Geometry equilibration failed,please see the output files in :'+str(macrotarget))    

  else:
    os.chdir(plgpath)
    os.chdir(macrotarget)   
    _run_legacy_command(mopac+' '+macrotarget+'/'+ownfile)
    yasara.ShowMessage('Calculation is complete and results are saved in :'+str(macrotarget)) 
#yasara.ShowMessage('Please use different project name for the calculations') 
yasara.plugin.end()

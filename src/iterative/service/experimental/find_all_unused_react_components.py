import os
import re
from collections import defaultdict

def find_tsx_files(root_dir):
    tsx_files = []
    excluded_dirs = ['node_modules', 'build', 'dist', 'env3']

    for root, dirs, files in os.walk(root_dir, topdown=True):
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        for file in files:
            if file.endswith('.tsx'):
                tsx_files.append(os.path.join(root, file))

    return tsx_files

def extract_exported_components(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        # Adjust the regex to capture default exports except for page.tsx files
        if 'page.tsx' not in file_path:
            components = set(re.findall(r'export (default class|default function|const) (\w+)|export (default) (\w+)', content))
        else:
            components = set(re.findall(r'export const (\w+) =', content))
        exported = set(filter(None, [item for sublist in components for item in sublist[1:]]))
        return exported

def scan_for_unused_components(tsx_files):
    exported_components = defaultdict(set)
    component_usage = defaultdict(bool)

    for tsx_file in tsx_files:
        components = extract_exported_components(tsx_file)
        for component in components:
            exported_components[component].add(tsx_file)
            component_usage[component] = False

    for component in exported_components:
        for tsx_file in tsx_files:
            if component_usage[component]:
                break
            if tsx_file in exported_components[component]:
                continue
            with open(tsx_file, 'r', encoding='utf-8') as file:
                if re.search(rf'\b{component}\b', file.read()):
                    component_usage[component] = True

    unused_components = [comp for comp, used in component_usage.items() if not used]
    return unused_components, exported_components

def create_report(unused_components, exported_components, tsx_files, report_filename):
    with open(report_filename, 'w') as file:
        file.write("React Components Usage Report\n")
        file.write("========================================\n")
        file.write(f"Scanned {len(tsx_files)} TSX Files:\n")
        for tsx_file in tsx_files:
            file.write(f"- {tsx_file}\n")
        file.write("\nExtracted Components:\n")
        for component, files in exported_components.items():
            file.write(f"{component} (Extracted from: {', '.join(files)})\n")
        file.write("\nUnused Components:\n")
        for component in unused_components:
            file.write(f"{component}\n")
    print(f"Report generated: {report_filename}")

def main():
    root_dir = '.'  # Replace this with the root directory of your project
    report_filename = 'unused_components_report.txt'
    
    tsx_files = find_tsx_files(root_dir)
    unused_components, exported_components = scan_for_unused_components(tsx_files)
    create_report(unused_components, exported_components, tsx_files, report_filename)

if __name__ == "__main__":
    main()

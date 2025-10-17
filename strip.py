#!/usr/bin/env python3
"""
Script to process KiCad footprint files by removing courtyards and/or designators.

This script processes .kicad_mod files and can:
  - Remove courtyard layers (F.CrtYd and B.CrtYd) - saves to APRLPrints-nofp.pretty
  - Remove designator (reference) fields - saves to APRLPrints-nod.pretty
  - Remove both courtyards and designators - saves to APRLPrints-nodnofp.pretty

Output files are saved with appropriate suffixes:
  - '-nofp' for footprints without courtyards
  - '-nod' for footprints without designators
  - '-nodnofp' for footprints without both designators and courtyards
"""

import os
import re
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def has_courtyard(content: str) -> bool:
    """
    Check if the KiCad file contains courtyard definitions.
    
    Args:
        content: The file content as a string
        
    Returns:
        True if courtyard layers are found, False otherwise
    """
    # Look for courtyard layer definitions
    courtyard_pattern = r'layer\s+"[FB]\.CrtYd"'
    return bool(re.search(courtyard_pattern, content))


def strip_courtyard_from_content(content: str) -> str:
    """
    Remove all courtyard-related elements from KiCad file content.
    
    This function removes complete geometric elements (fp_rect, fp_line, fp_poly, 
    fp_circle, fp_arc) that are on courtyard layers (F.CrtYd or B.CrtYd).
    
    Args:
        content: The file content as a string
        
    Returns:
        Content with courtyard elements removed
    """
    lines = content.split('\n')
    result_lines = []
    i = 0
    removed_count = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this line starts a geometric element
        # Common KiCad footprint geometric elements
        geom_match = re.match(r'^(\s*)\((fp_rect|fp_line|fp_poly|fp_circle|fp_arc)\b', line)
        
        if geom_match:
            # Find the complete element (up to its closing parenthesis)
            indent = geom_match.group(1)
            element_lines = [line]
            paren_count = line.count('(') - line.count(')')
            j = i + 1
            
            # Continue collecting lines until we balance parentheses
            while j < len(lines) and paren_count > 0:
                element_lines.append(lines[j])
                paren_count += lines[j].count('(') - lines[j].count(')')
                j += 1
            
            # Check if this element is on a courtyard layer
            element_content = '\n'.join(element_lines)
            if re.search(r'layer\s+"[FB]\.CrtYd"', element_content):
                # Skip this element (don't add to result)
                removed_count += 1
                i = j
                continue
            else:
                # Keep this element
                result_lines.extend(element_lines)
                i = j
                continue
        
        # If not a geometric element, keep the line
        result_lines.append(line)
        i += 1
    
    if removed_count > 0:
        logger.info(f"  Removed {removed_count} courtyard element(s)")
    
    return '\n'.join(result_lines)

# KiCAD will just re-add the designator.
# def remove_designator(content: str) -> str:
#     """
#     Remove the designator (reference) text field from the KiCad file content.
    
#     The designator is typically the 'REF**' or 'reference' field in KiCad footprints.
#     This function removes:
#     - Older format: (fp_text reference "REF**" ...)
#     - Newer format: (property "Reference" "REF**" ...)
    
#     Args:
#         content: The file content as a string
        
#     Returns:
#         Content with the designator (reference) field removed
#     """
#     lines = content.split('\n')
#     result_lines = []
#     i = 0
#     removed_count = 0
    
#     while i < len(lines):
#         line = lines[i]
        
#         # Check if this line starts a reference element (old or new format)
#         # Old format: (fp_text reference "REF**" ...
#         # New format: (property "Reference" "REF**" ...
#         fp_text_match = re.match(r'^(\s*)\(fp_text\s+reference\b', line)
#         property_match = re.match(r'^(\s*)\(property\s+"Reference"', line)
        
#         if fp_text_match or property_match:
#             # Find the complete element (up to its closing parenthesis)
#             element_lines = [line]
#             paren_count = line.count('(') - line.count(')')
#             j = i + 1
            
#             # Continue collecting lines until we balance parentheses
#             while j < len(lines) and paren_count > 0:
#                 element_lines.append(lines[j])
#                 paren_count += lines[j].count('(') - lines[j].count(')')
#                 j += 1
            
#             # Skip this element (don't add to result)
#             removed_count += 1
#             i = j
#             continue
        
#         # If not a reference element, keep the line
#         result_lines.append(line)
#         i += 1
    
#     if removed_count > 0:
#         logger.info(f"  Removed {removed_count} designator field(s)")
    
#     return '\n'.join(result_lines)


def process_file(input_path: Path, output_path: Path, strip_courtyard: bool = True, 
                 strip_designator: bool = False) -> bool:
    """
    Process a single KiCad footprint file.
    
    Args:
        input_path: Path to the input .kicad_mod file
        output_path: Path where the processed file should be saved
        strip_courtyard: If True, remove courtyard layers
        # strip_designator: If True, remove the reference designator field
        
    Returns:
        True if processing was successful, False otherwise
    """
    try:
        # Read the input file
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        processed_content = content
        modified = False
        
        # Strip courtyards if requested
        if strip_courtyard:
            if has_courtyard(content):
                logger.info(f"  Processing {input_path.name} (removing courtyards)...")
                processed_content = strip_courtyard_from_content(processed_content)
                modified = True
            else:
                logger.warning(f"  No courtyard found in {input_path.name}")
        
        # Strip designator if requested
        # if strip_designator:
        #     logger.info(f"  Processing {input_path.name} (removing designator)...")
        #     processed_content = remove_designator(processed_content)
        #     modified = True
        
        # Write the output file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(processed_content)
        
        if modified:
            logger.info(f"  Successfully created {output_path.name}")
        else:
            logger.info(f"  Copied {output_path.name} (no modifications needed)")
        return True
        
    except Exception as e:
        logger.error(f"  Error processing {input_path}: {e}")
        return False


def main():
    """Main function to process all KiCad footprint files."""
    # Define paths
    script_dir = Path(__file__).parent
    input_dir = script_dir / 'APRLPrints.pretty'
    
    # Check if input directory exists
    if not input_dir.exists():
        logger.error(f"Input directory not found: {input_dir}")
        sys.exit(1)
    
    # Find all .kicad_mod files
    kicad_files = list(input_dir.glob('*.kicad_mod'))
    
    if not kicad_files:
        logger.warning(f"No .kicad_mod files found in {input_dir}")
        sys.exit(0)
    
    logger.info(f"Found {len(kicad_files)} .kicad_mod file(s) to process")
    
    # Define processing configurations
    # Each config is a tuple of (suffix, output_dir_name, strip_courtyard, strip_designator)
    configs = [
        ('-nofp', 'APRLPrints-nofp.pretty', True, False),       # No footprint (courtyard)
        # ('-nod', 'APRLPrints-nod.pretty', False, True),         # No designator
        # ('-nodnofp', 'APRLPrints-nodnofp.pretty', True, True),  # No designator and no footprint
    ]
    
    overall_success = True
    
    for suffix, output_dir_name, strip_courtyard, strip_designator in configs:
        output_dir = script_dir / output_dir_name
        
        # Create output directory if it doesn't exist
        output_dir.mkdir(exist_ok=True)
        
        logger.info(f"\n{'='*50}")
        logger.info(f"Processing files for {output_dir_name}")
        logger.info(f"  Strip courtyards: {strip_courtyard}")
        # logger.info(f"  Strip designators: {strip_designator}")
        logger.info(f"{'='*50}")
        
        # Process each file
        success_count = 0
        for input_file in sorted(kicad_files):
            # Create output filename with suffix appended
            base_name = input_file.stem  # filename without extension
            output_filename = f"{base_name}{suffix}.kicad_mod"
            output_file = output_dir / output_filename
            
            if process_file(input_file, output_file, strip_courtyard, strip_designator):
                success_count += 1
        
        # Print summary for this configuration
        logger.info(f"\nProcessing complete for {output_dir_name}: {success_count}/{len(kicad_files)} files processed successfully")
        
        if success_count < len(kicad_files):
            overall_success = False
    
    # Print overall summary
    logger.info(f"\n{'='*50}")
    logger.info(f"All processing complete")
    logger.info(f"{'='*50}")
    
    if not overall_success:
        sys.exit(1)


if __name__ == '__main__':
    main()

# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import click
import json
from energyplus_viewfactors import ViewFactorEngine

from energyplus_viewfactors.__about__ import __version__

@click.command()
@click.argument('INPUT_EPJSON', type=click.File(mode='r'))
#@click.option('-x', '--x-length', type=click.FloatRange(0.0, min_open=True), show_default=True, default=32.0, help='Length of the grid in the x direction.')
#@click.option('-y', '--y-length', type=click.FloatRange(0.0, min_open=True), show_default=True, default=1.0, help='Length of the grid in the y direction.')
#@click.option('-z', '--z-length', type=click.FloatRange(0.0, min_open=False), show_default=True, default=0.0, help='Length of the grid in the z direction.')
#@click.option('-i', '--ni', type=click.IntRange(1), show_default=True, default=32, help='Number of cells in the i (x) direction.')
#@click.option('-j', '--nj', type=click.IntRange(1), show_default=True, default=32, help='Number of cells in the j (y) direction.')
#@click.option('-k', '--nk', type=click.IntRange(0), show_default=True, default=0, help='Number of cells in the k (z) direction.')
#@click.option('-o', '--output', type=click.File(mode='w'), show_default=False, default=None, help='File to write output to.')
@click.option('-o', '--output', type=click.Path(exists=True, writable=True), show_default=True, default='view3d', help='Directory to place outputs in.')
#@click.option('-f', '--format', type=click.Choice(['exo', 'plot3d']), default='exo', help='Specify format to use.')
@click.option('-v', '--verbose', is_flag=True, show_default=True, default=False, help='Operate verbosely.')
#@click.option('-t', '--top-wall-label', type=str, show_default=True, default='wall', help='Label for the wall boundary.')
#@click.option('-b', '--bottom-wall-label', type=str, show_default=True, default='centerline', help='Label for the centerline boundary.')
#@click.option('-l', '--left-label', type=str, show_default=True, default='inflow', help='Label for the left boundary.')
#@click.option('-r', '--right-label', type=str, show_default=True, default='outflow', help='Label for the right boundary.')
@click.option('-z', '--zone', type=str, multiple=True, show_default=False, default=None, help='Name of a zone to extract View3D inputs for, specify multiple to work on more than one zone.')
def extract(input_epjson, output, verbose, zone):
    """
    Extract View3D inputs from an EnergyPlus input file and (optionally) calculate the view factors.
    """
    vfe = ViewFactorEngine(fp=input_epjson)
    if verbose:
        click.echo('Model loaded successfully')
        click.echo(f'\tNumber of zones: {len(vfe.zones)}')
        click.echo(f'\tNumber of surfaces: {len(vfe.surfaces)}')
        click.echo(f'\tNumber of subsurfaces: {len(vfe.subsurfaces)}')
        click.echo(f'Zones to process: {', '.join(zone)}')
        for zn in zone:
            txt = '\n\t'.join(json.dumps(vfe.zones[zn], indent=4).splitlines())
            click.echo('\t' + txt + '\n\n')
        click.echo('Extracting zones...')
        vfe.extract(zones=zone, directory=output)
        click.echo('Done.')

@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=False)
@click.version_option(version=__version__, prog_name="energyplus-viewfactors")
def energyplus_viewfactors():
    pass

energyplus_viewfactors.add_command(extract)

#parser.add_argument("file",help="epjson file path",type=lambda x: is_valid_file(parser, x)) #Input epJSON file which should be used to prepere input for View3d file
#parser.add_argument("-z","--zone", help="Name/list of the zone if only chosen zones should be used to calculate view factor") 
#parser.add_argument("-r","--run",help="Run View3D to generate view factors and insert values into the epJSON file")
#parser.add_argument("-v","--view3d", help="View 3D default path")
#parser.add_argument("-o","--output",help="Write epJSON output to OUTFILE so that the original file is left unchanged")

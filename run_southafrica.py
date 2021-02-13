"""
Test for searching South Africa Parliament website for legal aid content.

The class legisSouthAfrica was originally generated by Selenium IDE.
However, it has been converted to a Chromedriver for ease of use,
and added lots of custom functionality.
"""

import argparse
import os
import sys
from pathlib import Path

import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from legiscrapor.legissouthafrica import legisSouthAfrica

docstring = """
Extract legislation PDFs from the website for
South African Parliament.
"""

webpage_help = """
Select from:
1=Constitution
2=Mandates
3=Acts
4=Other Bills
"""


def parse_args(args):
    """Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(description=docstring)
    parser.add_argument('webpage', metavar='webpage', type=int,
                        help='Webpage to process.' + webpage_help)
    parser.add_argument('--driver', '-d',
                        default=ChromeDriverManager().install(),
                        help='Path for Chromedriver')
    parser.add_argument('--path', '-p',
                        default=None,
                        help='Path for PDF downloads')

    args = parser.parse_args()
    return args


def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """
    args = parse_args(args)
    if args.path is not None:
        download_path = str(args.path)
    else:
        current_dir = Path(os.path.abspath(os.curdir))
        download_path = current_dir / 'south_africa_output'
        download_path = str(download_path)  # class wants strings for paths
        if not os.path.exists(download_path):
            os.mkdir(download_path)

    # setting up options for Chromedriver
    # mostly to ensure any PDF links automatically
    # download the PDFs to download_path
    options = webdriver.ChromeOptions()
    options.add_experimental_option('prefs', {
        "download.default_directory": download_path,  # Default dir downloads
        "download.prompt_for_download": False,  # to auto download the file
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True  # don't show PDF in chrome
    })

    pd.options.display.max_colwidth = 1000
    keywords = ['legal aid']  # TODO: take these as command-line options?

    # keywords = ['legal aid',
    #           'legal assistance',
    #           'legal service',
    #           'judicial assistance']

    new_za = legisSouthAfrica(args.driver, download_path, options)
    new_za.checkers()

    if args.webpage == 1:
        scrape(new_za, keywords, 'constit')
    elif args.webpage == 2:
        scrape(new_za, keywords, 'mandates')
    elif args.webpage == 3:
        scrape(new_za, keywords, 'acts')
    elif args.webpage == 4:
        scrape(new_za, keywords, 'bills')
    else:
        error_msg = 'ERROR: webpage integer indicator not found.'
        raise ValueError(error_msg + webpage_help)


def scrape(new_za, keywords: list, page_type: str):
    matches = new_za.run_bills(keywords)
    specs = 'SouthAfrica-' + page_type
    download_path = new_za.downloadPath + '/' + page_type
    if matches:
        print(matches)
        new_za.print_matches(matches, specs)
        new_za.delete_no_matches(specs, path=download_path)
    else:
        new_za.delete_unneeded_files('duplicates-nomatch-' + specs, [],
                                     files_path=download_path)

    new_za.delete_unneeded_files('duplicates-' + specs, [])
    new_za.teardown()


def run():
    main(sys.argv[1:])


if __name__ == '__main__':
    run()

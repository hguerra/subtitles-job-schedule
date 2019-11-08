# -*- coding: utf-8 -*-
"""
This is a skeleton file that can serve as a starting point for a Python
console script. To run this script uncomment the following lines in the
[options.entry_points] section in setup.cfg:

    console_scripts =
         subtitles = subtitles_job_schedule.subtitles_observer:run

Then run `python setup.py install` which will install the command `subtitles`
inside your current environment.
Besides console scripts, the header (i.e. until _logger...) of this file can
also be used as template for Python modules.
"""

import logging
import os
import time
from datetime import timedelta, datetime as dt

import schedule
from babelfish import Language
from dotmap import DotMap
from subliminal import download_best_subtitles, region, save_subtitles, scan_videos

__author__ = 'Heitor Carneiro'
__copyright__ = 'Heitor Carneiro'
__license__ = 'mit'

_date_formatter = '%Y-%m-%d'
_datetime_formatter = '%Y-%m-%d %H:%M:%S'
_logger = logging.getLogger(__name__)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = '[%(asctime)s] %(levelname)s:%(name)s:%(message)s'
    script_name = os.path.splitext(os.path.basename(__file__))[0]

    today = dt.now().strftime(_date_formatter)
    filename = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..', 'logs', '{}_{}.log'.format(today, script_name))
    )

    logging.basicConfig(level=loglevel, filename=filename, format=logformat, datefmt=_datetime_formatter)
    if loglevel <= logging.DEBUG:
        logging.getLogger().addHandler(logging.StreamHandler())


def search(path, languages):
    # configure the cache
    region.configure('dogpile.cache.dbm', arguments={'filename': 'cachefile.dbm'})

    # scan for videos newer than 2 weeks and their existing subtitles in a folder
    videos = set(scan_videos(path, age=timedelta(weeks=2)))

    # download best subtitles
    subtitles = download_best_subtitles(videos, languages)

    # save them to disk, next to the video
    for v in videos:
        _logger.debug('Saving {} ...'.format(v))
        save_subtitles(v, subtitles[v])


def job(videos, human_languages):
    try:
        if len(videos) == 0:
            raise ValueError('Video path is mandatory.')

        if len(human_languages) == 0:
            raise ValueError('Language is mandatory.')

        logging.debug('Searching subtitles at {}'.format(dt.now().strftime(_datetime_formatter)))

        languages = set()
        for iso_code in human_languages:
            language = None
            if isinstance(iso_code, str):
                language = Language(iso_code)
            elif isinstance(iso_code, tuple):
                if len(iso_code) == 1:
                    language = Language(iso_code[0])
                elif len(iso_code) == 2:
                    language = Language(iso_code[0], iso_code[1])

            if language is None:
                raise ValueError('Can not define language.')
            languages.add(language)

        for path in videos:
            search(path, languages)
    except:
        _logger.error('Fail to search subtitle.')


def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """
    setup_logging(args.loglevel)
    _logger.info('Starting observer...')

    schedule.every(args.minutes).minutes.do(job, videos=args.videos_path, human_languages=args.languages)
    while True:
        schedule.run_pending()
        time.sleep(1)


def run():
    """
    Entry point for console_scripts
    """
    default_args = DotMap(
        {
            'loglevel': logging.INFO,
            'minutes': 10,
            'videos_path': ['/tv', '/movies'],
            'languages': [('por', 'BR')]
        }
    )

    main(default_args)


if __name__ == '__main__':
    run()

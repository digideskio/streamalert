"""
Copyright 2017-present, Airbnb Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import re

from stream_alert.shared.logger import get_logger
from stream_alert.threat_intel_downloader.main import ThreatStream
from stream_alert_cli.helpers import user_input, save_parameter

LOGGER = get_logger(__name__)


def threat_intel_downloader_handler(options, config):
    """Configure Threat Intel Downloader from command line

    Args:
        options (argparse.Namespace): Parsed arguments
        config (CLIConfig): Loaded StreamAlert config

    Returns:
        bool: False if errors occurred, True otherwise
    """
    def _validate_options(options):
        if not options.interval:
            LOGGER.error('Missing command line argument --interval')
            return False

        if not options.timeout:
            LOGGER.error('Missing command line argument --timeout')
            return False

        if not options.memory:
            LOGGER.error('Missing command line argument --memory')
            return False

        return True

    if not options:
        return False

    if options.subcommand == 'enable':
        if not _validate_options(options):
            return False
        if config.add_threat_intel_downloader(vars(options)):
            return save_api_creds_info(config['global']['account']['region'])
    elif options.subcommand == 'update-auth':
        return save_api_creds_info(config['global']['account']['region'], overwrite=True)

def save_api_creds_info(region, overwrite=False):
    """Function to add API creds information to parameter store

    Args:
        info (dict): Required values needed to save the requested credentials
            information to AWS Parameter Store
    """
    # Get all of the required credentials from the user for API calls
    required_creds = {
        'api_user': {
            'description': ('API username to retrieve IOCs via API calls. '
                            'This should be an email address.'),
            'format': re.compile(r'^[a-zA-Z].*@.*')
        },
        'api_key': {
            'description': ('API key to retrieve IOCs via API calls. '
                            'This should be a string of 40 alphanumeric characters.'),
            'format': re.compile(r'^[a-zA-Z0-9]{40}$')
        }
    }

    creds_dict = {auth_key: user_input(info['description'], False, info['format'])
                  for auth_key, info in required_creds.iteritems()}

    description = ('Required credentials for the Threat Intel Downloader')

    # Save these to the parameter store
    saved = save_parameter(region, ThreatStream.CRED_PARAMETER_NAME,
                           creds_dict, description, overwrite)
    if saved:
        LOGGER.info('Threat Intel Downloader credentials were successfully '
                    'saved to parameter store.')
    else:
        LOGGER.error('Threat Intel Downloader credentials were not saved to '
                     'parameter store.')

    return saved

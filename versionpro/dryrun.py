"""
Dry Run Report Generation Module:
    - Produces various versions report
    - Uses threading for concurrent processing

Module Functions:
    - Package Current Version:
        Reports current version label assigned to code in current repository
    - PYPI Version:
        Looks in global pypi.python.org registry for package
        reports version if found
    - Incremental Version:
        Reports next incremental version ( (> pypi or project version) + 1 )
    - display_table:
        renders vpt table to cli stdout
"""

import os
import sys
import inspect

# 3rd party
from veryprettytable import VeryPrettyTable
from libtools.js import export_iterobject
from libtools import stdout_message
from libtools import Colors
from libtools import stdout_message, logd
from versionpro import Colors


try:
    from keyup.oscodes_unix import exit_codes
    os_type = 'Linux'
    splitchar = '/'                             # character for splitting paths (linux)
    text = Colors.BRIGHT_CYAN
except Exception:
    from keyup.oscodes_win import exit_codes    # non-specific os-safe codes
    os_type = 'Windows'
    splitchar = '\\'                            # character for splitting paths (windows)
    text = Colors.CYAN


cm = ColorMap()

# universal colors
yl = Colors.YELLOW + Colors.BOLD
fs = Colors.GOLD3
bd = Colors.BOLD
gn = Colors.BRIGHT_GREEN
btext = text + Colors.BOLD
bdwt = cm.bdwt
dgray = cm.dg1
frame = text
ub = Colors.UNBOLD
rst = Colors.RESET


tablespec = {
    'border': True,
    'header': True,
    'padding': 2,
    'field_max_width': 70
}

column_widths = {
    'project': 16,
    'pypi': 16,
    'incremental': 16,
}


def convert(dt):
    """Convert days to hours"""
    expiration_date = dt + KEYAGE_MAX
    now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
    if now < expiration_date and (expiration_date - now).days == 0:
        return (expiration_date - now).seconds / 3600


def display_table(table, exceptions, tabspaces=4):
    """
    Print Table Object offset from left by tabspaces
    """
    indent = ('\t').expandtabs(tabspaces)
    table_str = table.get_string()
    for e in table_str.split('\n'):
        print(indent + frame + e)
    sys.stdout.write(Colors.RESET + '\n')
    display_skipped(exceptions) if exceptions else print('')
    sys.stdout.write(Colors.RESET + '\n\n')
    return True


def format_remaining(days: int):
    """
        Formats days remaining value

    Returns:
        days (int) with appropriate color, spacing format applied
    """
    def spacing():
        s = ''
        for digit in str(days):
            s = s + ' '
        return s

    if (0 <= days < KEYAGE_WARNING):
        return cm.yl + spacing() + str(round(days)) + ' days' + rst
    elif days < 0:
        return cm.brd + spacing() + str(round(days / -1)) + 'd overdue' + rst
    else:
        return str(days) + ' days'


def print_header(title, indent=4, spacing=4):
    """
    Paints title header grid of a vpt Table
    """
    divbar = frame + '-'
    upbar = frame + '|' + rst
    ltab = '\t'.expandtabs(indent)              # lhs indentation of title bar
    spac = '\t'.expandtabs(7)                   # rhs indentation of legend from divider bar
    tab4 = '\t'.expandtabs(4)                   # space between legend items
    tab5 = '\t'.expandtabs(5)                   # space between legend items
    tab6 = '\t'.expandtabs(6)                   # space between legend items
    # construct legend
    valid = '{} valid{}'.format(gn + bd + 'o' + rst, tab5)
    near = '{} near expiration{}'.format(yl + bd + 'o' + rst, tab5)
    exp = '{} expired'.format(cm.brd + bd + 'o' + rst)
    # output header
    print('\n\n\n')
    print(tab4, end='')
    print(divbar * 119, end='')
    print('\n' + tab4 + upbar + frame + '\t|'.expandtabs(60) + rst + frame + '\t|'.expandtabs(56) + rst)
    print('{}{}{}{}{}{}'.format(tab4 + upbar + ltab, title + spac, valid, near, exp, tab6 + upbar))
    print(tab4 + upbar + frame + '\t|'.expandtabs(60) + rst + frame + '\t|'.expandtabs(56) + rst)
    return True


def spacing(days):
    s = ''
    for digit in str(days):
        s = s + ' '
    return s


def _postprocessing():
    return True


def setup_table(user_data, exception_list):
    """
    Renders Table containing data elements via cli stdout
    """
    # setup table
    x = VeryPrettyTable(
            border=tablespec['border'],
            header=tablespec['header'],
            padding_width=tablespec['padding']
        )

    x.field_names = [
        bdwt + 'Project Version' + frame,
        bdwt + 'PYPI Version' + frame,
        bdwt + 'Incremental Version' + frame,
    ]

    # cell max width
    x.max_width[bdwt + '' + frame] = column_widths['project'] + column_widths['pypi'] + column_widths['incremental']
    x.max_width[bdwt + 'Project Version' + frame] = column_widths['project']
    x.max_width[bdwt + 'PYPI Version' + frame] = column_widths['pypi']
    x.max_width[bdwt + 'Incremental Version' + frame] = column_widths['incremental']

    # cell min = max width
    x.min_width[bdwt + '' + frame] = column_widths['project'] + column_widths['pypi'] + column_widths['incremental']
    x.min_width[bdwt + 'Project Version' + frame] = column_widths['project']
    x.min_width[bdwt + 'PYPI Version' + frame] = column_widths['pypi']
    x.min_width[bdwt + 'Incremental Version' + frame] = column_widths['incremental']

    # cell alignment
    x.align[bdwt + 'Project Version' + frame] = 'c'
    x.align[bdwt + 'PYPI Version' + frame] = 'c'
    x.align[bdwt + 'Incremental Version' + frame] = 'c'

    # populate table
    for k, v in user_data.items():

            dt = v['CreateDate']
            expired = expired_keys(v['CreateDate'])
            _days = time_remaining(dt)
            k = truncate_fields(k)
            v = truncate_fields(v)

            #  key credentials are either expired (age > KEYAGE_MAX) or valid
            profilename = cm.brd + k + rst if expired else k
            user = cm.brd + v['iam_user'] + rst if expired else v['iam_user']
            accountId = cm.brd + v['account'] + rst if expired else v['account']

            x.add_row(
                [
                    rst + profilename + frame,
                    rst + user + frame,
                    rst + accountId + frame,
                ]
            )

    # Table
    vtab_int = 9
    vtab = '\t'.expandtabs(vtab_int)
    msg = '{}AWS Identity Access Key Expiration Report{}{}|{}'.format(btext, rst + frame, vtab, rst)
    print_header(title=msg, indent=10, spacing=vtab_int)
    display_table(x, exception_list, tabspaces=4)
    return _postprocessing()


def truncate_fields(element):
    """
        Truncates table field data to align with max column width

    Returns:
        truncated element, TYPE: dict or str
    """
    if isinstance(element, dict):
        for k, v in element.items():
            for name, width in column_widths.items():
                if k == name and k != 'CreateDate':
                    element[k] = v[:width]
        return element
    return element[:column_widths['ProfileName']]


def prepare_reportdata(debug=False):
    """
        Prints out key expiration info for all profilenames associated with
        the primary profilename given to access the account information

    """
    data, aliases = {}, {}
    exceptions = []

    if debug:
        export_iterobject(affiliations)

    for k, v in affiliations.items():

        account = v['account']

        try:
            r = None
            client = boto3_session(service='iam', profile=k)
            r = client.list_access_keys()
            key_metadata = r['AccessKeyMetadata']

            if debug:
                stdout_message(
                    message='Key information received for profile {}'.format(bd + k + rst),
                    prefix='OK'
                )

        except ClientError as e:
            fname = inspect.stack()[0][3]
            logger.info('{}: Unable to list key info for profile {}. Error {}'.format(fname, k, e))
            exceptions.append(k)
            continue

        try:

            if aliases.get(account):
                alias = aliases[account]
            else:
                # human readable name of the account
                alias = client.list_account_aliases()['AccountAliases'][0]

                # store identified aliases
                aliases[account] = alias

        except ClientError:
            alias = ''
        except IndexError:
            alias = account

        accountId = alias or account
        iam_user = key_metadata[0]['UserName']
        status = key_metadata[0]['Status']
        metadata = key_metadata[0]['CreateDate']

        data[k] = {
            'account': accountId,
            'iam_user': iam_user,
            'status': status,
            'CreateDate': metadata
        }

        logger.info('IAM User {} key info found for AWS account {}'.format(iam_user, accountId))
    return data, exceptions

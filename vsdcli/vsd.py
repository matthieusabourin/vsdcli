#!/usr/bin/env python

import argparse
import sys

sys.path.append("../")


def main(argv=sys.argv):

    default_parser = argparse.ArgumentParser(description="CLI for VSD Software Development Kit", add_help=False)
    default_parser.add_argument('-v', '--verbose', help='Activate verbose mode', action='store_true')
    default_parser.add_argument('--username', help='username to get an api key or set `VSD_USERNAME` in your variable environment')
    default_parser.add_argument('--password', help='password to get an api key or set `VSD_PASSWORD` in your variable environment')
    default_parser.add_argument('--api', help='URL of the API endpoint or set `VSD_API_URL` in your variable environment')
    default_parser.add_argument('--version', help='Version of the API or set `VSD_API_VERSION` in your variable environment')
    default_parser.add_argument('--enterprise', help='Name of the enterprise to connect or set `VSD_ENTERPRISE` in your variable environment')
    default_parser.add_argument('--json', help='Add this option get a JSON output or set VSD_JSON_OUTPUT="True"', action='store_true')

    parser = argparse.ArgumentParser(description="Usage: vsd {command} {arguments}")
    subparsers = parser.add_subparsers(dest="command",
                                       title='All available commands')

    # List Command
    list_parser = subparsers.add_parser('list', parents=[default_parser], help="List all objects")
    list_parser.add_argument('list', help="name of the object to list")
    list_parser.add_argument('--in', dest='parent_infos', nargs=2, help="Specify the parent name and its uuid")
    list_parser.add_argument('-f', '--filter', dest='filter', help="Specify a filter predicate")
    list_parser.add_argument('-x', '--fields', dest='fields', help="Specify output fields", nargs='+', type=str)

    # Show Command
    show_parser = subparsers.add_parser('show', parents=[default_parser], help="Show a specific object details")
    show_parser.add_argument('show', help="name of the object to show")
    show_parser.add_argument('-i', '--id', dest='id', help='Identifier of the object to show', required=True)
    show_parser.add_argument('-x', '--fields', dest='fields', help="Specify output fields", nargs='+', type=str)

    # Create Command
    create_parser = subparsers.add_parser('create', parents=[default_parser], help="Create a new object")
    create_parser.add_argument('create', help='name of the object to create')
    create_parser.add_argument('--in', dest='parent_infos', nargs=2, help="Specify the parent name and its uuid")
    create_parser.add_argument('-p', '--params', dest='params', nargs='*', help='List of Key=Value parameters', required=True)

    # Update Command
    update_parser = subparsers.add_parser('update', parents=[default_parser], help="Update an existing object")
    update_parser.add_argument('update', help='name of the object to update')
    update_parser.add_argument('-i', '--id', dest='id', help='Identifier of the object to show', required=True)
    update_parser.add_argument('-p', '--params', dest='params', nargs='*', help='List of Key=Value parameters', required=True)

    # Delete Command
    delete_parser = subparsers.add_parser('delete', parents=[default_parser], help="Delete an existing object")
    delete_parser.add_argument('delete', help='name of the object to update')
    delete_parser.add_argument('-i', '--id', dest='id', help='Identifier of the object to show', required=True)

    # Resources Command
    objects_parser = subparsers.add_parser('objects', parents=[default_parser], help="View all VSD objects")
    objects_parser.add_argument('-f', '--filter', dest='filter', help='Specify a filter')
    objects_parser.add_argument('-p', '--parent', dest='parent', help='Specify a parent resource')
    objects_parser.add_argument('-c', '--child', dest='child', help='Option to display children of a resource')

    args = parser.parse_args()

    from commands import VSDCommand
    VSDCommand.execute(args)


if __name__ == '__main__':
    main()
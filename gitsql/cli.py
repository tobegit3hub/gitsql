#!/usr/bin/env python3

import argparse
import logging
from . import openmldb_importer

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser(prog='gitsql')
parser.add_argument('--repo', required=True, help='The path of git repository to import')
parser.add_argument('--openmldb_zk', default="127.0.0.1:2181", help='The zookeeper cluster of OpenMLDB')
parser.add_argument('--openmldb_path', default="/openmldb", help='The zookeeper path of OpenMLDB')

subparsers = parser.add_subparsers(dest='command')
parser_init = subparsers.add_parser('init', help='Initialize databases for git repo')
parser_load = subparsers.add_parser('load', help='Load data for git repo into databases')
parser_delete = subparsers.add_parser('delete', help='Delete databases for git repo')


def main():
  args = parser.parse_args()
  importer = openmldb_importer.OpenmldbImporter(args.openmldb_zk, args.openmldb_path, args.repo)

  if (args.command == "init"):
    importer.create_db_and_tables()
  elif (args.command == "load"):
    importer.load_git_data_to_db()
  elif (args.command == "delete"):
    importer.drop_db_and_tables()
  else:
    logging.fatal("Unsupported command, exit now")
    exit(-1)


if __name__ == "__main__":
  main()

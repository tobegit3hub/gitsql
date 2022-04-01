#!/usr/bin/env python3

import argparse
import openmldb_importer

parser = argparse.ArgumentParser(prog='gitsql')
parser.add_argument('--repo', required=True, help='The path of git repository to import')
parser.add_argument('--openmldb_zk', default="127.0.0.1:2181", help='The zookeeper cluster of OpenMLDB')
parser.add_argument('--openmldb_path', default="/openmldb", help='The zookeeper path of OpenMLDB')

def main():

  args = parser.parse_args()

  importer = openmldb_importer.OpenmldbImporter(args.openmldb_zk, args.openmldb_path, args.repo)

if __name__ == "__main__":
  main()

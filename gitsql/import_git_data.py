#!/usr/bin/env python3

import logging
import openmldb.dbapi
from git import Repo



def create_db_and_tables(cursor):
  logging.info("Try to create gitsql database")
  cursor.execute("CREATE DATABASE IF NOT EXISTS gitsql")

  cursor.execute("CREATE TABLE commit (hexsha string, author string, email string, date int64, summary string,, size int, insertions int, deletions int, lines int, files int)")

def insert_commit_data(cursor, commit):
  sql = """INSERT INTO commit VALUES("{}", "{}", "{}", {}, "{}", {}, {}, {}, {}, {})""".format(
    commit.hexsha,
    # TODO(tobe): Use prepared statement
    commit.author.name.replace('"', '\\"'),
    commit.author.email.replace('"', '\\"'),
    commit.committed_date,
    commit.summary.replace('"', '\\"'),
    commit.size,
    commit.stats.total["insertions"],
    commit.stats.total["deletions"],
    commit.stats.total["lines"],
    commit.stats.total["files"]
  )
  try:
    cursor.execute(sql)
  except Exception as e:
    logging.error("Fail to execute sql: {}, get error: {}".format(sql, e))


def main():
  print("Start of main")

  connection = openmldb.dbapi.connect("gitsql", "127.0.0.1:2181", "/openmldb")
  cursor = connection.cursor()

  # Initialize database and tables
  create_db_and_tables(cursor)

  repo = Repo("/Users/tobe/code/4pd/OpenMLDB")
  if repo.bare:
    print("Repo does not exist and exit now")
    return

  commit_num = 0
  for commit in repo.iter_commits():
    commit_num += 1
    # Insert commit info to table
    insert_commit_data(cursor, commit)
    #import ipdb;ipdb.set_trace()

  print("Total commit number: " + str(commit_num))

if __name__ == "__main__":
  main()

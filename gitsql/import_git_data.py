#!/usr/bin/env python3

import logging
import openmldb.dbapi
from git import Repo



def create_db_and_tables(cursor):
  logging.info("Try to create gitsql database")
  cursor.execute("CREATE DATABASE IF NOT EXISTS gitsql")

  logging.info("Try to create commit table")
  cursor.execute("CREATE TABLE commit (hexsha string, author string, email string, date int64, summary string,, size int, insertions int, deletions int, lines int, files int)")

  logging.info("Try to create branch table")
  cursor.execute("CREATE TABLE branch (name string, path string, commit string, remote bool, valid bool)")


def insert_commit_row(cursor, commit):
  sql = """INSERT INTO commit VALUES ("{}", "{}", "{}", {}, "{}", {}, {}, {}, {}, {})""".format(
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


def insert_branch_row(cursor, branch):
  sql = """INSERT INTO branch VALUES ("{}", "{}", "{}", {}, {})""".format(
    branch.name,
    branch.path,
    branch.commit.hexsha,
    branch.is_remote(),
    branch.is_valid()
  )

  try:
    cursor.execute(sql)
  except Exception as e:
    logging.error("Fail to execute sql: {}, get error: {}".format(sql, e))


def import_commit_data(repo, cursor):
  commit_num = 0
  for commit in repo.iter_commits():
    commit_num += 1
    # Insert commit info to table
    insert_commit_row(cursor, commit)
  print("Total commit number: " + str(commit_num))


def import_branch_data(repo, cursor):
  branch_num = 0
  for branch in repo.branches:
    branch_num += 1
    # Insert branch info to table
    insert_branch_row(cursor, branch)
  print("Total branch number: " + str(branch_num))


def main():

  connection = openmldb.dbapi.connect("gitsql", "127.0.0.1:2181", "/openmldb")
  cursor = connection.cursor()

  # Initialize database and tables
  create_db_and_tables(cursor)

  repo = Repo("/Users/tobe/code/4pd/OpenMLDB")
  if repo.bare:
    print("Repo does not exist and exit now")
    return

  import_commit_data(repo, cursor)
  import_branch_data(repo, cursor)


if __name__ == "__main__":
  main()

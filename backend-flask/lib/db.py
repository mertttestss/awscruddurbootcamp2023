from psycopg_pool import ConnectionPool
import os
import re
import sys
from flask import current_app as app

class Db:
  def __init__(self):
    self.init_pool()

  def template(self,*args):
    pathing = list((app.root_path,'db','sql',) + args)
    pathing[-1] = pathing[-1] + ".sql"

    template_path = os.path.join(*pathing)

    green = '\033[92m'
    no_color = '\033[0m'
    print("\n")
    print(f'{green} Load SQL Template: {template_path} {no_color}')

    with open(template_path, 'r') as f:
      template_content = f.read()
    return template_content

  def init_pool(self):
  # we want to commit data such as an insert
  # be sure to check for RETURNING in all uppercases
    def print_params(self,params):
      blue = '\033[94m'
      no_color = '\033[0m'
      print(f'{blue} SQL Params:{no_color}')
      for key, value in params.items():
        print(key, ":", value)

    def print_sql(self,title,sql):
      cyan = '\033[96m'
      no_color = '\033[0m'
      print(f'{cyan} SQL STATEMENT-[{title}]------{no_color}')
      print(sql)
    def query_commit(self, sql, params={}):
        self.print_sql('commit with returning', sql)
        try:
            with self.pool.connection() as conn:
                cur = conn.cursor()
                cur.execute(sql, params)
                
                if "RETURNING" in sql.upper():
                    result = cur.fetchone()
                    if result:
                        conn.commit()
                        return result[0]  # UUID'yi döndür
                    else:
                        conn.rollback()
                        raise ValueError("No rows returned")
                
                conn.commit()
        except Exception as err:
            self.print_sql_err(err)
            raise
    # when we want to return a json object
    def query_array_json(self,sql,params={}):
      self.print_sql('array',sql)

      wrapped_sql = self.query_wrap_array(sql)
      with self.pool.connection() as conn:
        with conn.cursor() as cur:
          cur.execute(wrapped_sql,params)
          json = cur.fetchone()
          return json[0]
    # When we want to return an array of json objects
    def query_object_json(self,sql,params={}):

      self.print_sql('json',sql)
      self.print_params(params)
      wrapped_sql = self.query_wrap_object(sql)

      with self.pool.connection() as conn:
        with conn.cursor() as cur:
          cur.execute(wrapped_sql,params)
          json = cur.fetchone()
          if json == None:
            "{}"
          else:
            return json[0]
    def query_wrap_object(self,template):
      sql = f"""
      (SELECT COALESCE(row_to_json(object_row),'{{}}'::json) FROM (
      {template}
      ) object_row);
      """
      return sql
    def query_wrap_array(self,template):
      sql = f"""
      (SELECT COALESCE(array_to_json(array_agg(row_to_json(array_row))),'[]'::json) FROM (
      {template}
      ) array_row);
      """
      return sql
    def print_sql_err(self,err):
      # get details about the exception
      err_type, err_obj, traceback = sys.exc_info()

      # get the line number when exception occured
      line_num = traceback.tb_lineno

      # print the connect() error
      print ("\npsycopg ERROR:", err, "on line number:", line_num)
      print ("psycopg traceback:", traceback, "-- type:", err_type)

      # print the pgcode and pgerror exceptions
      print ("pgerror:", err)
      print ("pgcode:", err, "\n")


db = Db()

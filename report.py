import argparse
import datetime

import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor

TEAM2USERS = {
    'BI Team': {
        'demyd_chernenko',
        'dhirman',
        'hairong_gu',
        'julie_preston',
        'julie_robinson',
        'nicholas_malos',
        'preethy_joy',
        'tableau',
        'trevor_mhariwa',
        'valentina',
        'viktor_bondyriev'
    },
    'Data Team': {
        'dmytro_trunykov',
        'sudhir_shekhsaria'
    },
    'DevOps': {
        'ademydov',
        'adw',
        'devops',
        'dserdiuk',
        'juan_jose',
        'mnations',
        'rbovda',
        'vsuslikov'
    },
    'Product': {
        'katie'
    },
    'Risk': {
        'ian_fade',
        'joe_widjaja',
        'judy_zhu',
        'levente_szabo',
        'mykola_danylenko',
        'ravi_trivedi',
        'risk',
        'rockford_stoller',
        'santiago_figueroa',
        'seetha',
        'tejas_trivedi'
    },
    'Root User': {
        'cognicaladmin'
    },
    'Sales': {
        'john_baran'
    },
    'Tech': {
        'alex_dzhus',
        'alex_kessler',
        'ben',
        'fallon_mcneill',
        'freny_patel',
        'irene_ganusevich',
        'jesse_zahrt',
        'julia_povarova',
        'kshitij_sachdeva',
        'lms',
        'lms_user_1',
        'newrelic',
        'nrahman',
        'shashikala_rajaji',
        'shrey_kumar',
        'shubhansh_jain',
        'sunil',
        'vidya_patil',
        'yevhen_lytvyn'
    }
}


def username2teamname(username: str) -> str:
    for team, members in TEAM2USERS.items():
        if username in members:
            return team
    return None


def report_lms_db(conn: object, fname: str) -> None:
    with conn.cursor() as cur:
        query = '''
            SELECT
               t.user_name AS \"User Name\", t.member_of AS \"Member Of\",
               t.super_user AS \"Super User\", t.status AS \"Status\"
            FROM (
               SELECT
                  r.rolname AS user_name,
                  ARRAY(
                      SELECT b.rolname
                      FROM pg_catalog.pg_auth_members m
                      JOIN pg_catalog.pg_roles b ON (m.roleid = b.oid)
                      WHERE m.member = r.oid
                  ) as member_of,
                  CASE
                      WHEN r.rolsuper THEN 'Yes'
                      ELSE 'No'
                  END AS super_user,
                  CASE
                      WHEN r.rolvaliduntil < now() THEN 'Inactive'
                      ELSE 'Active'
                  END AS status
               FROM pg_catalog.pg_roles r
               WHERE
                  r.rolname NOT LIKE 'pg_%'
                  AND r.rolname NOT LIKE 'lambda_%'
            ) AS t
            WHERE ARRAY_LENGTH(t.member_of, 1) > 0 OR t.super_user = 'Yes'
            ORDER BY t.super_user DESC, t.user_name ASC
        '''
        cur.execute(query)
        rows = cur.fetchall()
        for r in rows:
            r['Member Of'] = ' '.join(r['Member Of'])
            r['Team'] = username2teamname(r['User Name'])
        df = pd.DataFrame.from_dict(rows)
        df.to_excel(fname, index=False, sheet_name='Cognical DB Access')
        print(query)


def report_lms_users(conn: object, fname: str) -> None:
    with conn.cursor() as cur:
        query = '''
            SELECT
               id, last_login::timestamp without time zone, is_superuser, 
               username, first_name, last_name, 
               email, date_joined::timestamp without time zone 
            FROM auth_user 
            WHERE 
            is_staff=True AND is_active=True 
            AND EXTRACT('Year' FROM last_login) >= 
               EXTRACT('Year' FROM CURRENT_DATE) 
            ORDER BY is_superuser DESC, username ASC
        '''
        cur.execute(query)
        rows = cur.fetchall()
        df = pd.DataFrame.from_dict(rows)
        df.to_excel(fname, index=False)
        print(query)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--lms-db-host', type=str,
                        default='prod-rds.katapult.com',
                        help='A host of the "cognicaldb".')
    parser.add_argument('--lms-db-port', type=int,
                        default=5432,
                        help='A port number of the host.')
    parser.add_argument('--lms-db-name', type=str,
                        default='cognicaldb',
                        help='A name of the "cognicaldb" database.')
    parser.add_argument('--lms-db-user', type=str, required=True,
                        help='A DB user name.')
    parser.add_argument('--lms-db-password', type=str, required=True,
                        help='A DB user password.')
    parser.add_argument('--out-file', type=str, required=True,
                        help='A file name to store result.')
    parser.add_argument('report_type', metavar='REPORT TYPE',
                        choices=('db_users', 'lms_users'),
                        help='A report type. One of: db | lms')

    args = parser.parse_args()

    with psycopg2.connect(
            host=args.lms_db_host, port=args.lms_db_port,
            dbname=args.lms_db_name, user=args.lms_db_user,
            password=args.lms_db_password,
            cursor_factory=RealDictCursor) as conn:
        print(f'\n *** Current date: {datetime.datetime.now()}\n\n')
        if args.report_type == 'db_users':
            report_lms_db(conn, args.out_file)
        elif args.report_type == 'lms_users':
            report_lms_users(conn, args.out_file)
        else:
            raise RuntimeError(f'Unexpected report type: {args.report_type}')

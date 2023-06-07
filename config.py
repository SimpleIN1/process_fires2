import os
from dotenv import load_dotenv

load_dotenv()

db_name = os.getenv('db_name')
db_user = os.getenv('db_user')
db_password = os.getenv('db_password')
db_port = os.getenv('db_port')
db_host = os.getenv('db_host')
db_listen_event = os.getenv('db_listen_event')

db_url = f'postgresql://{db_user}:{db_password}@{db_host}/{db_name}'

ftp_server = os.getenv('ftp_server')
ftp_login = os.getenv('ftp_login')
ftp_password = os.getenv('ftp_password')

monitor_dir = '/home/py-user/monitor_dir'
    # '/home/grigoriy/PycharmProjects/UsuallyPythonProject/process_fire/monitor_dir'


name_function_insert_district = 'function_insert_district'
name_trigger_settlement_ins = '__settlement_ins__'
name_function_send_notify_process = 'send_notify_process'
name_trigger_fire_value_change = '__fire_value_change__'

psql_row_create_function_insert_district = \
"""
create FUNCTION {0}() RETURNS trigger as ${1}$
declare
    district_identity INT;
begin
    select into district_identity d.id from district as d where ST_Intersects(NEW.point::geometry, d.poly::geometry) = 't';
    NEW.district_id := district_identity;
    return NEW;
end;
${1}$ language  plpgsql;
""".format(name_function_insert_district, name_trigger_settlement_ins)

psql_row_create_trigger_settlement_ins = \
"""
create trigger {} before INSERT on settlement
    for each row execute procedure {}();
""".format(name_trigger_settlement_ins, name_function_insert_district)

psql_row_create_function_send_notify_process = \
"""
create or replace function {}() returns trigger
as $log$
declare
    event json;
BEGIN

    if (lower(tg_op) = 'insert') then
        event = json_build_object('id', new.id, 'longitude', new.longitude, 'latitude', new.latitude)::varchar;
    end if;

    perform pg_notify('{}', event::text);

    return NULL;
END;
$log$
language plpgsql;
""".format(name_function_send_notify_process, db_listen_event) #'events'

psql_row_create_trigger_fire_value_change = \
"""
create trigger {0} after insert on fire_value for each row
    execute function {1}();
""".format(name_trigger_fire_value_change, name_function_send_notify_process)

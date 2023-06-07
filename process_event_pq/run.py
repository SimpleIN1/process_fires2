from shapely.geometry import Point

from process_fire.process_event_pq.process_fire_value import ProcessFirePoint
from psycopg_notify import Psycopg2Notify


def main():
    pn = Psycopg2Notify()
    pn.run_event_loop()


if __name__ == '__main__':
    main()


from process_fire.loader_data.load import LoadToDataBase


def main():
    ldb = LoadToDataBase()
    # db.drop_all_tables()

    ldb.write_subject_shp()
    ldb.write_district()
    ldb.write_settlement_with_point_polygon()
    ldb.write_technogenic_zone()
    ldb.write_tag_to_regions()


if __name__ == '__main__':
    main()
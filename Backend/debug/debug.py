
orig_metadata = {'metadata': {'music': [{'title': 'We Are The World', 'album': {'name': 'We Are The World'}, 'release_date': '1985-01-01', 'label': 'USA for Africa', 'db_begin_time_offset_ms': 26680, 'db_end_time_offset_ms': 37720, 'external_metadata': {}, 'sample_end_time_offset_ms': 11040, 'play_offset_ms': 38120, 'result_from': 3, 'duration_ms': 427000, 'acrid': '9ebae2b8b503caf150d50a886049b0ed', 'external_ids': {}, 'score': 100, 'artists': [{'name': 'U.S.A. for Africa'}], 'sample_begin_time_offset_ms': 0, 'genres': [{'name': 'Pop'}]}, {'title': 'We Are The World  (Những ca khúc bất tử)', 'album': {'name': 'We Are The World  (Những ca khúc bất tử)'}, 'db_begin_time_offset_ms': 26160, 'db_end_time_offset_ms': 36220, 'external_metadata': {}, 'sample_end_time_offset_ms': 10060, 'play_offset_ms': 37580, 'result_from': 3, 'score': 100, 'duration_ms': 432000, 'acrid': 'dd6461dac5e75d3ce1d4a60d6283a8f7', 'external_ids': {}, 'label': 'USA for Africa', 'artists': [{'name': 'Michael Jackson'}], 'release_date': '2009-06-29', 'sample_begin_time_offset_ms': 0, 'genres': [{'id': '59', 'name': 'Pop'}]}, {'title': 'Humanism Means to Be Human', 'album': {'name': 'Breaking the Pattern'}, 'db_begin_time_offset_ms': 0, 'db_end_time_offset_ms': 11020, 'external_metadata': {}, 'sample_end_time_offset_ms': 11020, 'play_offset_ms': 11780, 'result_from': 3, 'duration_ms': 416000, 'acrid': 'd941ef9f6db6177b043cb75d9dedc8a0', 'external_ids': {}, 'score': 100, 'artists': [{'name': 'Abhijit Naskar'}], 'release_date': '2018-10-09', 'label': 'Abhijit Naskar // The Neuroscientist', 'sample_begin_time_offset_ms': 0}], 'timestamp_utc': '2024-03-11 23:53:27'}, 'result_type': 0, 'status': {'msg': 'Success', 'code': 0, 'version': '1.0'}, 'cost_time': 0.026999950408936}
test = {'genres': [{'name': 'Pop'}]}

def get_song_metadata():
        filtered_metadata = []
        for metadata in orig_metadata.get("metadata").get("music"):
            filtered_metadata.append({
                "title": metadata.get("title", ""),
                "album": metadata.get("album", {}).get("name", ""),
                "artists": [x.get("name") for x in metadata.get("artists", [])],
                "release_date": metadata.get("release_date", "")
                })
            
        return filtered_metadata

print(get_song_metadata())

# print({"genres": [x.get("name") for x in test.get("genres")]})
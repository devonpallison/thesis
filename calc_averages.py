from Markov import *

def get_avg_batting_score_2017():
    counts = {}
    counts[strike] = 0
    counts[foul] = 0
    counts[ball] = 0
    counts[single] = 0
    counts[double] = 0
    counts[triple] = 0
    counts[home_run] = 0
    counts[field_out] = 0

    for subdir, dirs, files in os.walk("/Users/devonallison/code/Monopoly/src/main/thesis/data/rosters"):
        for file in files:
            if file.endswith(".txt"):
                file_path = "/Users/devonallison/code/Monopoly/src/main/thesis/data/rosters/" + file
                print("Reading file {}".format(file_path))
                with open(file_path) as openFile:
                    lines = openFile.readlines()
                    print(lines)
                    for line in lines:
                        full_name = line.strip()
                        print("Found name {}".format(full_name))
                        name = full_name.split()
                        print("First name: {} last name: {}".format(name[0], name[1]))

                        try:
                            stats = None
                            batter_id = get_player_id(name[0], name[1])
                            if(batter_id > 0): #if batter id is -1, the player was not found
                                stats = get_batter_stats("1900-01-01", "2017-01-01", batter_id)
                        except Exception as e:
                            # do nothing if we found an error
                            print("Error while getting stats for {} ".format(full_name))
                            print("Error {} ".format(e))

                        if stats is not None:
                            counts[strike] += len(stats.loc[stats["description"] == strike])
                            counts[foul] += len(stats.loc[stats["description"] == foul])
                            counts[ball] += len(stats.loc[stats["description"] == ball])
                            counts_hit = stats.loc[stats["description"] == hit]
                            counts[single] += len(counts_hit.loc[counts_hit["events"] == single])
                            counts[double] += len(counts_hit.loc[counts_hit["events"] == double])
                            counts[triple] += len(counts_hit.loc[counts_hit["events"] == triple])
                            counts[home_run] += len(counts_hit.loc[counts_hit["events"] == home_run])
                            counts[field_out] += len(counts_hit.loc[counts_hit["events"] == field_out])

            print("Done processing file {}".format(file))
            print("Current counts: {}".format(counts))
    stats = {}
    num_pitches = sum(counts.values())
    stats[strike] = counts[strike] / num_pitches
    stats[foul] = counts[foul] / num_pitches
    stats[ball] = counts[ball] / num_pitches
    stats[single] = counts[single] / num_pitches
    stats[double] = counts[double] / num_pitches
    stats[triple] = counts[triple] / num_pitches
    stats[home_run] = counts[home_run] / num_pitches
    stats[field_out] = counts[field_out] / num_pitches

    return stats

#results:
#counts = {'called_strike': 331528, 'foul': 325552, 'ball': 670185, 'single': 86956, 'double': 26763, 'triple': 3137, 'home_run': 15987, 'field_out': 223157}
#{'called_strike': 0.19695532194871276, 'foul': 0.1934050788200313, 'ball': 0.39814586532720636, 'single': 0.051659126756630716, 'double': 0.015899457304702467, 'triple': 0.0018636400091488863, 'home_run': 0.009497613269449551, 'field_out': 0.13257389656411794}
print(get_avg_batting_score_2017())
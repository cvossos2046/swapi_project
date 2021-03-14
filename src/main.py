import requests
import pickle
import sys
from datetime import datetime
import os


def search(name):
    """Function that searches the given name in people data

    Args:
        name (str): The name for search

    Returns:
        list: A list of dictionaries which contains the information of all
              characters that were found as well as the time of search.
    """
    # get the data from people
    response = requests.get("https://swapi.dev/api/people/")
    # time of request
    time = str(datetime.now())
    characters_list = response.json()['results']

    searched_char_list = []
    searched_char = {}
    for character in characters_list:
        if name.lower() in character['name'].lower():
            split_str = character['name'].lower().split(' ')
            for el in split_str:
                if name.lower()[0] == el[0]:
                    searched_char = {"name": character['name'],
                                     "height": character['height'],
                                     "mass": character['mass'],
                                     "birth_year": character['birth_year'],
                                     "homeworld": character['homeworld'],
                                     "time": time}
                    searched_char_list.append(searched_char)
    # if the name wasn't found return only the time of search
    if len(searched_char_list) == 0:
        searched_char_list.append({"time": time})
    return searched_char_list


def world(homeworld_url):
    """Function that takes all the usefull information about the planet where
       the searched character lives.

    Args:
        homeworld_url (str): The url of the planet for search

    Returns:
        dict: Dictionary which contains the name, the population, the year and
              day duration in planet against earth year and day, and the time
              of search
    """
    earth_rotation_period = 24
    earth_orbital_period = 365

    # get the data from planets
    response = requests.get(homeworld_url)
    planets_dict = response.json()
    # time of request
    time = str(datetime.now())

    try:
        orbital_period = int(planets_dict["orbital_period"])
        rotation_period = int(planets_dict["rotation_period"])
        year_factor = orbital_period / earth_orbital_period
        day_factor = rotation_period / earth_rotation_period
        year_factor = round(year_factor, 2)
        day_factor = round(day_factor, 2)
    except ValueError:
        year_factor = "unknown"
        day_factor = "unknown"

    output_str = "Homeworld\n---------\n{}\n{}\n\n".format(planets_dict["name"], planets_dict["population"])
    world_day_year_msg = "On {}, 1 year on earth is {} years and 1 day is {} days\n".format(planets_dict["name"], year_factor, day_factor)
    output_str = output_str + world_day_year_msg
    world_output_dict = {"output": output_str, "time": time}
    return world_output_dict


def print_save_search(searches, character, save, world_option):
    """Function that prints the results of a search, and save the search in
       case that is a new one.

    Args:
        searches (list): A list of dictionaries which contains the information
                         about all the searches that have been made
        character (dictionary): A Dictionary with the character information
        save (bool): Is True if we have a new search, so it has to be saved,
                     otherwise is False
        world_option (bool): Is True if the search was made with "--world"
                             option, otherwise is False
    """
    if len(character) == 1:
        print("The force is not strong within you")
        world_output = ""
        time = character["time"]
        if save is True:
            searches.append({"name": name,
                             "world_option": world_option,
                             "time": time,
                             "character": character,
                             "world_output": world_output})
            pickle.dump(searches, open("searches.pickle", "wb"))

    else:
        if world_option is False:
            world_output = ""
            time = character['time']
            if save is True:
                searches.append({"name": name,
                                 "world_option": world_option,
                                 "time": time,
                                 "character": character,
                                 "world_output": world_output})
                pickle.dump(searches, open("searches.pickle", "wb"))
            print("Name: {}" .format(character['name']))
            print("Height: {}" .format(character['height']))
            print("Mass: {}" .format(character['mass']))
            print("Birth Year: {}\n" .format(character['birth_year']))
            print("cached: {}\n" .format(character['time']))
        else:
            if save is True:
                url = character["homeworld"]
                world_dict = world(url)
                world_output = world_dict["output"]
                time = world_dict["time"]
                searches.append({"name": name,
                                 "world_option": world_option,
                                 "time": time,
                                 "character": character,
                                 "world_output": world_output})
                pickle.dump(searches, open("searches.pickle", "wb"))
                print("Name: {}" .format(character['name']))
                print("Height: {}" .format(character['height']))
                print("Mass: {}" .format(character['mass']))
                print("Birth Year: {}\n" .format(character['birth_year']))
                print(world_output)
                print("cached: {}\n" .format(time))
            else:
                save = False
                print("Name: {}" .format(character['name']))
                print("Height: {}" .format(character['height']))
                print("Mass: {}" .format(character['mass']))
                print("Birth Year: {}\n" .format(character['birth_year']))
                for search_dict in searches:
                    if character == search_dict["character"] and world_option == search_dict["world_option"]:
                        print(search_dict["world_output"] + "\n")
                        print("cached: {}\n" .format(search_dict["time"]))


def clean_cache():
    """ Function that deletes all the searches that have been made
    """
    if os.path.exists("searches.pickle"):
        os.remove("searches.pickle")
        print("removed cache")

    else:
        print("Cache is empty")


def searches_visualization():
    """Function that prints all the searches that have been made, the results
       and the time of search
    """
    try:
        searches = pickle.load(open("searches.pickle", "rb"))
        for search_dict in searches:
            if search_dict["world_option"] is True:
                print("Search: {} --world\n".format(search_dict["name"]))
            else:
                print("Search: {}\n".format(search_dict["name"]))
            character = search_dict["character"]
            save = False
            if len(character) == 1:
                print("Result\nThe force is not strong within you \n\n")
                print("cached: {}\n".format(character["time"]))
            else:
                print("Result")
                print_save_search(searches, character, save, search_dict["world_option"])
    except (OSError, IOError):
        print("Cache is empty")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and str(sys.argv[1]) == "search" and len(sys.argv) < 5:
        name = str(sys.argv[2])
        if name != "":
            try:
                searches = pickle.load(open("searches.pickle", "rb"))
            except (OSError, IOError):
                searches = []
                pickle.dump(searches, open("searches.pickle", "wb"))

            if len(sys.argv) == 3:
                world_option = False
            elif str(sys.argv[3]) == "--world":
                world_option = True
            else:
                print("Wrong arguments!")
                exit(0)

            if len(searches) == 0:
                chararacters_list = search(name)
                save = True
                for character in chararacters_list:
                    print_save_search(searches, character, save, world_option)
            else:
                searched_names = []
                for search_dict in searches:
                    searched_names.append(search_dict["name"])
                if name not in searched_names:
                    chararacters_list = search(name)
                    save = True
                    for character in chararacters_list:
                        print_save_search(searches, character, save, world_option)
                else:
                    '''
                    here the name has already been searched, but we have to
                    check if it has been searched with or without --world in
                    order to conclude if this search has already been saved
                    '''
                    search_exists = False
                    for search_dict in searches:
                        if search_dict["name"] == name:
                            if search_dict["world_option"] == world_option:
                                search_exists = True
                                break

                    save = not search_exists
                    temp_searches = searches[:]
                    for search_dict in temp_searches:
                        if search_dict["name"] == name:
                            if search_exists is False:
                                print_save_search(searches, search_dict["character"], save, world_option)
                            else:
                                if search_dict["world_option"] == world_option:
                                    print_save_search(searches, search_dict["character"], save, world_option)

    elif len(sys.argv) == 3 and str(sys.argv[1]) == "cache" and str(sys.argv[2]) == "--clean":
        clean_cache()

    elif len(sys.argv) == 2 and str(sys.argv[1]) == "visualization":
        searches_visualization()

    else:
        print("Wrong arguments!")

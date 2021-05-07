import os

def modeChooser():
    modes = ["DAP", "DDAP"]
    mode = ""
    while mode.upper() not in modes:
        mode = input("Choose problem type to solve DAP or DDAP[" + DEFAULT_MODE + "]: ") or DEFAULT_MODE
    return mode

def stopCriterionChooser():
    criteria = ["TIME", "GENERATIONS", "MUTATIONS", "NO_PROGRESS"]
    print("Choose stop criterion:")
    for crit in criteria:
        print(crit)

    criterion = ""
    while criterion.upper() not in criteria:
        criterion = input("Choose stop criterion[" + DEFAULT_STOP_CRITERION + "]: ") or DEFAULT_STOP_CRITERION
    return criterion

def populationChooser():
    population = 0
    while population < 1:
        try:
            population = int(input("Set population size[" + str(DEFAULT_POPULATION) + "]: ") or DEFAULT_POPULATION)
        except ValueError:
            continue
    return population

def stopCriterionTimeChooser():
    time = 0
    while time < 1:
        try:
            time = int(input("Set time limit in seconds[" + str(DEFAULT_STOP_CRITERION_TIME) + "]: ") or DEFAULT_STOP_CRITERION_TIME)
        except ValueError:
            continue
    return time

def stopCriterionGenerationsChooser():
    generations = 0
    while generations < 1:
        try:
            generations = int(input("Set generations limit[" + str(DEFAULT_STOP_CRITERION_GENERATIONS) + "]: ") or DEFAULT_STOP_CRITERION_GENERATIONS)
        except ValueError:
            continue
    return generations

def stopCriterionMutationsChooser():
    mutations = 0
    while mutations < 1:
        try:
            mutations = int(input("Set mutations limit[" + str(DEFAULT_STOP_CRITERION_MUTATIONS) + "]: ") or DEFAULT_STOP_CRITERION_MUTATIONS)
        except ValueError:
            continue
    return mutations

def stopCriterionNoProgressGeneratonsChooser():
    generations = 0
    while generations < 1:
        try:
            generations = int(input("Set no progress generations limit[" + str(DEFAULT_STOP_CRITERION_NO_PROGRESS_GENERATIONS) + "]: ") or DEFAULT_STOP_CRITERION_NO_PROGRESS_GENERATIONS)
        except ValueError:
            continue
    return generations

def generatorSeedChooser():
    seed = 0
    while seed < 1:
        try:
            seed = int(input("Set generator seed[" + str(DEFAULT_GENERATOR_SEED) + "]: ") or DEFAULT_GENERATOR_SEED)
        except ValueError:
            continue
    return seed

def geneCrossoverProbabilityChooser():
    probability = -1
    while probability < 0:
        try:
            probability = float(input("Set gene crossover probability[" + str(DEFAULT_GENE_CROSSOVER_PROBABILITY) + "]: ") or DEFAULT_GENE_CROSSOVER_PROBABILITY)
            if probability > 1:
                continue
        except ValueError:
            continue
    return probability

def geneMutationProbabilityChooser():
    probability = -1
    while probability < 0:
        try:
            probability = float(input("Set gene mutation probability[" + str(DEFAULT_GENE_MUTATION_PROBABILITY) + "]: ") or DEFAULT_GENE_MUTATION_PROBABILITY)
            if probability > 1:
                continue
        except ValueError:
            continue
    return probability

def fileChooser():
    allfiles = os.listdir(INPUT_DIRECTORY_PATH)
    files=[]
    for f in allfiles:
        if f.endswith(".txt"):
            files.append(f)

    print("Choose input file: ")
    for index, f in enumerate(files):
        print(str(index + 1) + ": " + f)

    print()
    filename = ""
    while not filename:
        try:
            i = int(input("Choose file[1]: ") or 1)
            if i < 1  or i > len(files):
                continue
            filename = INPUT_DIRECTORY_PATH + "/" + files[i - 1]
        except ValueError:
            continue
    return filename

# Main program function
if __name__ == '__main__':

    # Initialize default values
    DEFAULT_MODE = "DAP"
    DEFAULT_POPULATION = 500
    DEFAULT_GENE_CROSSOVER_PROBABILITY = 0.5
    DEFAULT_GENE_MUTATION_PROBABILITY = 0.05
    DEFAULT_STOP_CRITERION = "TIME"
    DEFAULT_STOP_CRITERION_TIME = 500
    DEFAULT_STOP_CRITERION_GENERATIONS = 1000
    DEFAULT_STOP_CRITERION_MUTATIONS = 5000
    DEFAULT_STOP_CRITERION_NO_PROGRESS_GENERATIONS = 50
    DEFAULT_GENERATOR_SEED = 19258
    INPUT_DIRECTORY_PATH = "input"

    # User choose file, mode, population, gene crossover and mutation probability, generator seed and stop criterion
    INPUT_FILE_PATH = fileChooser()
    MODE = modeChooser()
    POPULATION = populationChooser()
    GENE_CROSSOVER_PROBABILITY = geneCrossoverProbabilityChooser()
    GENE_MUTATION_PROBABILITY = geneMutationProbabilityChooser()
    GENERATOR_SEED = generatorSeedChooser()
    STOP_CRITERION = stopCriterionChooser()
    STOP_CRITERION_VALUE = 0

    if STOP_CRITERION == "TIME":
        STOP_CRITERION_VALUE = stopCriterionTimeChooser()
    elif STOP_CRITERION == "GENERATIONS":
        STOP_CRITERION_VALUE = stopCriterionGenerationsChooser()
    elif STOP_CRITERION == "MUTATIONS":
        STOP_CRITERION_VALUE = stopCriterionMutationsChooser()
    elif STOP_CRITERION == "NO_PROGRESS":
        STOP_CRITERION_VALUE = stopCriterionNoProgressGeneratonsChooser()
    else:
        print("Ha! You found a bug. Report it to project maintainer :)")
        print("Program panic. Exiting...")
        quit()


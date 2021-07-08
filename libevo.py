import copy
import random
from datetime import datetime
from time import time
from typing import List

from libtopo import NetworkTopology, Chromosome, Gene, Codon


class EvolutionaryOptimizer:

    def __init__(self, network: NetworkTopology, mode, population, crossover_probability, mutation_probability, seed,
                 stop_criterion, criterion_value, input_file_path):
        self.network = network
        self.mode = mode
        self.population_size = population
        self.crossover_probability = crossover_probability
        self.mutation_probability = mutation_probability
        self.seed = seed
        self.stop_criterion = stop_criterion
        self.criterion_max_value = criterion_value
        self.input_file_path = input_file_path
        self.start_time = 0
        self.generations_count = 0
        self.mutations_count = 0
        self.current_progress = 0
        self.cost_function = self.set_cost_function()
        self.best_chromosome_ever = Chromosome()
        self.best_result = 999999999
        self.former_best = 999999999
        self.elapsed_time = 0

    def check_remaining_time(self):
        elapsed_time = time() - self.start_time
        print("\r", end="")
        print("Generation: " + str(self.generations_count) + ", Best solution: " + str(self.best_result))
        print("Working... " + str(elapsed_time / self.criterion_max_value * 100) + "%", end="")
        return self.criterion_max_value - elapsed_time

    def check_remaining_generations(self):
        print("\r", end="")
        print("Generation: " + str(self.generations_count) + ", Best solution: " + str(self.best_result))
        print("Working... " + str(self.generations_count / self.criterion_max_value * 100) + "%, Generation: " + str(
            self.generations_count) + "/" + str(self.criterion_max_value), end="")
        return self.criterion_max_value - self.generations_count

    def check_remaining_mutations(self):
        print("\r", end="")
        print("Generation: " + str(self.generations_count) + ", Best solution: " + str(self.best_result))
        print("Working... " + str(self.mutations_count / self.criterion_max_value * 100) + "%, " + str(
            self.mutations_count) + "/" + str(self.criterion_max_value) + " mutations", end="")
        return self.criterion_max_value - self.mutations_count

    def check_remaining_progress(self):
        if self.best_result < self.former_best:
            self.current_progress = 0
        else:
            self.current_progress += 1

        self.former_best = self.best_chromosome_ever.cost

        print("\r", end="")
        print("Generation: " + str(self.generations_count) + ", Best solution: " + str(self.best_result))
        print("Working. No result change in last " + str(self.current_progress) + "/" + str(
            self.criterion_max_value) + " iterations...", end="")
        return self.criterion_max_value - self.current_progress

    def set_stop_function(self):
        stop_function = ""
        if self.stop_criterion == "TIME":
            return self.check_remaining_time
        elif self.stop_criterion == "GENERATIONS":
            return self.check_remaining_generations
        elif self.stop_criterion == "MUTATIONS":
            return self.check_remaining_mutations
        else:
            return self.check_remaining_progress

    def set_cost_function(self):
        if self.mode == "DAP":
            return self.assign_cost_function_DAP
        else:
            return self.assign_cost_function_DDAP

    def distribute_randomly(self, size, count):
        distribution = [0] * size

        for i in range(count):
            distribution[random.randint(0, size - 1)] += 1

        return distribution

    def assign_cost_function_DAP(self, chromosome):
        demand_units = [0] * len(self.network.links)
        for gene in chromosome.genes:
            for codon in gene.codons:
                for link in codon.path.link_ids:
                    demand_units[link - 1] += codon.demand_units

        link_overload_modules = [0] * len(self.network.links)
        for link in self.network.links:
            link_overload_modules[link.id] = demand_units[link.id] - (link.modules_number * link.link_module)

        chromosome.cost = max(link_overload_modules)

    def assign_cost_function_DDAP(self, chromosome):
        link_demands = [0] * len(self.network.links)

        for gene in chromosome.genes:
            for codon in gene.codons:
                for link in codon.path.link_ids:
                    link_demands[link - 1] += codon.demand_units

        link_cost = [0] * len(self.network.links)
        for link in self.network.links:
            link_cost[link.id] = -(-link_demands[link.id] // link.link_module) * link.module_cost

        chromosome.cost = sum(link_cost)

    def generate_initial_population(self):
        population = []

        for chromosome_index in range(self.population_size):
            chromosome = Chromosome()
            for demand in self.network.demands:
                gene = Gene()
                distribution = self.distribute_randomly(len(demand.paths), demand.demand_volume)
                for path_index, path in enumerate(demand.paths):
                    gene.codons.append(Codon(path, distribution[path_index]))

                chromosome.genes.append(gene)

            self.cost_function(chromosome)
            population.append(chromosome)

        return population

    def find_best_solution(self, population):
        best = 99999
        solution = 0
        for chromosome in population:
            if chromosome.cost < best:
                best = chromosome.cost
                solution = chromosome
        self.best_result = best
        return solution

    def create_new_population(self, population):
        for chromosome in population:
            for gene in chromosome:
                if int(random.uniform(0, 1) + self.mutation_probability):
                    self.mutate(gene)
                    self.mutations_count += 1

    def create_new_members(self, population):
        new_members = []
        a = 0

        min = 99999
        max = -99999
        for chromosome in population:
            if chromosome.cost > max:
                max = chromosome.cost

            if chromosome.cost < min:
                min = chromosome.cost

        if min == max:
            for chromosome in population:
                chromosome.normalized_fitness_function = 1
            a = len(population)
        else:
            for chromosome in population:
                chromosome.normalized_fitness_function = (max - chromosome.cost) / (max - min)
                a += chromosome.normalized_fitness_function

        selected = []

        p = self.crossover_probability * len(population) / a

        for chromosome in population:
            if random.random() < p * chromosome.normalized_fitness_function:
                selected.append(chromosome)

        selected_copy = copy.deepcopy(selected)

        for i in range(int(len(selected_copy) / 2)):
            a = random.randint(0, len(selected_copy) - 1)
            chromosome_a = selected_copy[a]
            selected_copy.pop(a)

            a = random.randint(0, len(selected_copy) - 1)
            chromosome_b = selected_copy[a]
            selected_copy.pop(a)

            result = self.crossover(chromosome_a, chromosome_b)
            population.append(result[0])
            population.append(result[1])

    def mutate(self, gene):
        if len(gene.codons) < 2:
            return

        a = random.randint(0, len(gene.codons) - 1)
        b = random.randint(0, len(gene.codons) - 1)

        while not gene.codons[a].demand_units:
            a = random.randint(0, len(gene.codons) - 1)

        while a == b:
            b = random.randint(0, len(gene.codons) - 1)

        gene.codons[a].demand_units -= 1
        gene.codons[b].demand_units += 1

        self.mutations_count += 1

    def apply_mutations(self, population):
        for chromosome in population:
            for gene in chromosome.genes:
                if random.random() < self.mutation_probability:
                    self.mutate(gene)

            self.cost_function(chromosome)

    def crossover(self, chromosome_a, chromosome_b):
        result = [Chromosome(), Chromosome()]
        for i in range(len(chromosome_a.genes)):
            if random.random() < 0.5:
                result[0].genes.append(chromosome_a.genes[i])
                result[1].genes.append(chromosome_b.genes[i])
            else:
                result[0].genes.append(chromosome_b.genes[i])
                result[1].genes.append(chromosome_a.genes[i])

        self.cost_function(result[0])
        self.cost_function(result[1])
        return result

    def trim_population(self, population: List[Chromosome]):
        population.sort(key=lambda x: x.cost)
        del population[500:]

    def parse_chromosome(self, chromosome):
        link_demands = [0] * len(self.network.links)

        for gene in chromosome.genes:
            for codon in gene.codons:
                for link in codon.path.link_ids:
                    link_demands[link - 1] += codon.demand_units

        link_modules = [0] * len(self.network.links)
        for link in self.network.links:
            link_modules[link.id] = -(-link_demands[link.id] // link.link_module)

        output = str(len(self.network.links)) + "\n"

        for link in self.network.links:
            output += "\n"
            output += str(link.id + 1)
            output += " "
            output += str(link_demands[link.id - 1])
            output += " "
            output += str(link_modules[link.id - 1])

        output += "\n\n"

        output += str(len(chromosome.genes))  # no of demands
        output += "\n"

        for index, gene in enumerate(chromosome.genes):
            output += "\n"
            output += str(index + 1)  # demand id
            output += " "
            output += str(len(gene.codons))  # no of demand paths

            for ind, codon in enumerate(gene.codons):
                output += "\n"
                output += str(ind + 1)
                output += " "
                output += str(codon.demand_units)

            output += "\n"
        return output

    def optimize(self):
        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y_%H:%M:%S")
        log_file = open(dt_string + ".log", "w")

        random.seed(self.seed)
        population = self.generate_initial_population()
        print("Generating initial population success!")
        self.generations_count = 0

        stop_function = self.set_stop_function()
        generations_best = copy.deepcopy(self.find_best_solution(population))
        self.best_chromosome_ever = copy.deepcopy(generations_best)
        best_chromosome_ever_iteration = self.generations_count
        best_chromosome_ever_time = 0
        best = self.parse_chromosome(generations_best)
        log_file.write(best)
        self.start_time = time()
        remaining_progress = stop_function()

        if remaining_progress <= 0:
            print("Best solution was: " + str(self.best_chromosome_ever.cost) + " found at iteration " + str(
                best_chromosome_ever_iteration))
            log_file.write("\n\n\nFile path: " + self.input_file_path)
            log_file.write("\nProblem type: " + self.mode)
            log_file.write("\nRandom generator seed: " + str(self.seed))
            log_file.write("\nBest result cost function value: " + str(self.best_chromosome_ever.cost))
            log_file.write(
                "\nBest result found at iteration no. " + str(best_chromosome_ever_iteration) + " in 0 seconds")
            log_file.write("\nPopulation size: " + str(self.population_size) + "\nGene mutation probability: " + str(
                self.mutation_probability) + "\nCrossover probability: " + str(self.crossover_probability) + "\n\n")
            log_file.write("Best solution details:\n\n")
            log_file.write(self.parse_chromosome(self.best_chromosome_ever))
            return self.best_chromosome_ever

        while remaining_progress > 0:
            self.create_new_members(population)
            self.apply_mutations(population)
            self.trim_population(population)

            self.generations_count += 1
            generations_best = copy.deepcopy(self.find_best_solution(population))
            if generations_best.cost < self.best_chromosome_ever.cost:
                self.best_chromosome_ever = copy.deepcopy(generations_best)
                best_chromosome_ever_iteration = self.generations_count
                best_chromosome_ever_time = time() - self.start_time
            best = self.parse_chromosome(generations_best)
            log_file.write("\n\n")
            log_file.write(best)
            remaining_progress = stop_function()

        print("Best solution was: " + str(self.best_chromosome_ever.cost) + " found at iteration " + str(
            best_chromosome_ever_iteration))

        log_file.write("\n\n\nFile path: " + self.input_file_path)
        log_file.write("\nProblem type: " + self.mode)
        log_file.write("\nRandom generator seed: " + str(self.seed))
        log_file.write("\nBest result cost function value: " + str(self.best_chromosome_ever.cost))
        log_file.write("\nBest result found at iteration no. " + str(best_chromosome_ever_iteration) + " in " + str(
            best_chromosome_ever_time) + " seconds")
        log_file.write("\nPopulation size: " + str(self.population_size) + "\nGene mutation probability: " + str(
            self.mutation_probability) + "\nCrossover probability: " + str(self.crossover_probability) + "\n\n")
        log_file.write("Best solution details:\n\n")
        log_file.write(self.parse_chromosome(self.best_chromosome_ever))

        return self.best_chromosome_ever

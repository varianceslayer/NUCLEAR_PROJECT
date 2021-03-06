from data_extraction import DATA_DIRECTORY, get_dataframes
import random
import os
import math
import matplotlib.pyplot as plt
import seaborn as sns
from nucleus_probability import get_nucleus_probability_dict, nucleus_probs
from collision import get_collision_prob_dict,elastic_collision_energy,inelastic_collision_energy


DATA_DIRECTORY_NUCLEUS = 'data'
DATA_DIRECTORY_D2O = 'data/D2O_collision'
DATA_DIRECTORY_U_238 = 'data/U_238_collision'
DATA_DIRECTORY_Zr = 'data/Zr_collision'
DATA_DIRECTORY_D = 'data/D_collision'
DATA_DIRECTORY_O = 'data/O_collision'

class MultiplicationFactor:
    """class to run a Monte Carlo Simulation to generate a Multiplication factor for a given reaction
    """

    def __init__(self,steps,D2O=True):
        """constructor for the class

        Args:
            steps (int): number of steps in dividing the energies
            D2O (bool, optional): whether to combine of separate D2O. Defaults to True.
        """
        # All input variables
        self.steps = steps
        self.D2O = D2O
        print("Reading data")
        self.nucleus_prob_dataframe = get_dataframes(DATA_DIRECTORY_NUCLEUS)
        self.D2O_dataframe = get_dataframes(DATA_DIRECTORY_D2O)
        self.U_238_dataframe = get_dataframes(DATA_DIRECTORY_U_238)
        self.Zr_dataframe = get_dataframes(DATA_DIRECTORY_Zr)
        self.D_dataframe = get_dataframes(DATA_DIRECTORY_D)
        self.O_dataframe = get_dataframes(DATA_DIRECTORY_O)
        print("Reading data done")

    @staticmethod
    def pdf(x):
        """return the value at any x according to pdf of nuetrons

        Args:
            x (int): the value at which pdf is to be evaluated

        Returns:
            int: y value of pdf
        """
        return 0.771*math.sqrt(x)*(math.exp(-0.776*x))

    @staticmethod
    def generate_random_with_dist(population, weights):
        """generates random number according to the distribution

        Args:
            population (list): list of x values
            weights (list): list of y values

        Returns:
            int: a random value according to the assigned weights
        """
        
        return random.choices(population, weights)

    def fix_init_nuetron_energy(self):
        """function to fix the initial energy of a nuetron in the simulation

        Returns:
            int: randomly selected initial energy of a nuetron
        """
        population_list = [(7/self.steps)*step for step in range(1,self.steps)]
        weights_list = [self.pdf(step) for step in population_list]
        init_energy = self.generate_random_with_dist(population_list, weights_list)

        return init_energy[0]*10e6


    def generate_choices_probability(self, energy, nuclei_prob_dict=None):
        """function to generate event choices randomly for a given nuetron energy

        Args:
            energy ([int]): initial nuetron energy
            nuclei_prob_dict (dict, optional): probabilities of choices. Defaults to None.

        Returns:
            string: choices from a given list
        """
        if not nuclei_prob_dict:
            nuclei_prob_dict = get_nucleus_probability_dict(energy,self.nucleus_prob_dataframe,D2O=self.D2O)
        weights = []
        population = []

        for key in nuclei_prob_dict.keys():
            weights.append(nuclei_prob_dict[key])
            population.append(key)

        return self.generate_random_with_dist(population, weights)

    def generate_collision_type(self,init_energy,nuclei):
        """function to generate the type of collission which the atom undergoes

        Args:
            init_energy (int): initial nuetron energy
            nuclei (string): the nucleus which will collide

        Returns:
            string: the type of collison
        """
        if nuclei=='D2O':
            col_prob_dict = get_collision_prob_dict(init_energy, self.D2O_dataframe)
            return self.generate_choices_probability(init_energy,nuclei_prob_dict=col_prob_dict)[0]
        if nuclei=='U_238':

            col_prob_dict = get_collision_prob_dict(init_energy, dataframe=self.U_238_dataframe, nucleus='U_238')
            return self.generate_choices_probability(init_energy,nuclei_prob_dict=col_prob_dict)[0]
        if nuclei=='Zr':
            col_prob_dict = get_collision_prob_dict(init_energy, dataframe=self.Zr_dataframe,nucleus='Zr')
            return self.generate_choices_probability(init_energy, nuclei_prob_dict=col_prob_dict)[0]
        if nuclei=='D':
            col_prob_dict = get_collision_prob_dict(init_energy,self.D_dataframe,nucleus='D')
            return self.generate_choices_probability(init_energy,nuclei_prob_dict=col_prob_dict)[0]
        if nuclei=='O':
            col_prob_dict = get_collision_prob_dict(init_energy, self.O_dataframe,nucleus='O')
            return self.generate_choices_probability(init_energy, nuclei_prob_dict=col_prob_dict)[0]
        return 'in_progress'

    @staticmethod
    def energy_post_collision(init_energy, collision_type, nucleus):
        """function to return the final energy after a collision

        Args:
            init_energy (int): intial energy of nuetron
            collision_type (string): type of collision
            nucleus (string): the nucleus type

        Returns:
            int: final nuetron energy
        """
        print('updating')
        print(init_energy)
        if(collision_type=='elastic'):
            return elastic_collision_energy(init_energy,nucleus)
        if(collision_type=='inelastic'):
            return inelastic_collision_energy(init_energy)
        if(collision_type=='capture'):
            return 0

    def run_simulation(self):
        """Runs the Monte Carlo simulation
        """
        number_of_nuetrons = int(input('Please enter number of nuetrons: '))
        dead = 0
        D2O_capture = 0
        Zr_capture = 0
        U_238_capture = 0


        print("Alocating nuetron energies")
        nuetron_energies = [self.fix_init_nuetron_energy() for count_nuetron in range(number_of_nuetrons)]
        print('Done. Starting Simulation now')
        fission_count = 0
        captured_nuetrons = 0
        print(nuetron_energies)
        for nuetron_number in range(len(nuetron_energies)):
            nuetron_energy = nuetron_energies[nuetron_number]
            

            is_alive_nuetron = True
            
            while(is_alive_nuetron):
                
                if(nuetron_energy<0.000001):
                    is_alive_nuetron = False
                    dead += 1
                    continue
                nucleus_prob = self.generate_choices_probability(nuetron_energy)[0]

                if nucleus_prob == 'Zr':

                    collision_type = self.generate_collision_type(nuetron_energy,nucleus_prob)

                    print(nucleus_prob + ' ' + collision_type)
                    if collision_type == 'capture':
                        captured_nuetrons += 1
                        Zr_capture += 1
                        is_alive_nuetron = False
                        continue
                    nuetron_energy = self.energy_post_collision(nuetron_energy,collision_type,nucleus_prob)


                if nucleus_prob == 'U_235':
                    fission_count += random.choices([2,3],[0.5,0.5])[0]
                    is_alive_nuetron = False
                    continue
                if nucleus_prob == 'D2O':
                    collision_type = self.generate_collision_type(nuetron_energy,nucleus_prob)
                    print(nucleus_prob + ' ' + collision_type)
                    if collision_type == 'capture':
                        captured_nuetrons += 1
                        D2O_capture += 1
                        is_alive_nuetron = False
                        continue
                    nuetron_energy = self.energy_post_collision(nuetron_energy,collision_type,nucleus_prob)
                    continue
                if nucleus_prob == 'D':
                    collision_type = self.generate_collision_type(nuetron_energy,nucleus_prob)
                    print(nucleus_prob + ' ' + collision_type)
                    if collision_type == 'capture':
                        captured_nuetrons += 1
                        D2O_capture += 1
                        is_alive_nuetron = False
                        continue
                    nuetron_energy = self.energy_post_collision(nuetron_energy,collision_type,nucleus_prob)
                if nucleus_prob == 'O':
                    collision_type = self.generate_collision_type(nuetron_energy,nucleus_prob)
                    print(nucleus_prob + ' ' + collision_type)
                    if collision_type == 'capture':
                        captured_nuetrons += 1
                        D2O_capture += 1
                        is_alive_nuetron = False
                        continue
                    nuetron_energy = self.energy_post_collision(nuetron_energy,collision_type,nucleus_prob)
                    print('updated ',nuetron_energy)
                if nucleus_prob == 'U_238':
                    if nuetron_energy<1000:
                        collision_type = 'capture'
                    else:
                        collision_type = 'inelastic'
                    print(nucleus_prob + ' ' + collision_type)
                    if collision_type == 'capture':
                        captured_nuetrons += 1
                        U_238_capture += 1
                        is_alive_nuetron = False
                        continue
                    nuetron_energy = self.energy_post_collision(nuetron_energy,collision_type,nucleus_prob)
        print('Multiplication Factor: ',fission_count/number_of_nuetrons)
        print('captured nuetrons ',captured_nuetrons)
        print('nuetrons capture in Zr ',Zr_capture)
        print('nuetrons capture in D2O',D2O_capture)
        print('nuetrons capture in U_238 ',U_238_capture)
        print('nuetrons dead ',dead)
        print('new nuetrons from fissioned nuetrons ',fission_count)


if __name__ == "__main__":
    print('Installing Dependencies')
    os.system('pip install -r requirements.txt')
    print('Dependencies Installation Done')
    Simulation_Instance = MultiplicationFactor(10000,D2O=True)
    Simulation_Instance.run_simulation()



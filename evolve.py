"""
Microbe - Microbial Simulation
Copyright (C) 2009 James Garnon
"""

from __future__ import division
import random


class Evolve(object):
    """
    Manages the evolutional process.
    """

    def genetics(self, inherit=None, mutation_rate=0.5,
                 genome=None, alleles=None):
        """
        Set genetics of organism.
        Arguments:
        inherit - contain copy of self.gene, otherwise, organism
        genetic makeup set randomly from possibilities in alleles;
        mutation_rate - rate at which heritable genes are mutated;
        genome - number of genes;
        alleles - ranges from which gene settings will be chosen.
        """
        if self.matrix.evolution and genome:     #evolve trait parameters
            self.inherit = inherit
            gene = {}
            mutation = random.random() < mutation_rate    #if inherit with mutation
            if not inherit or mutation:     #set genes chosen randomly from alleles
                for genex in range(1,genome+1):
                    gene[genex] = random.randrange(*alleles[genex])
                if mutation:
                    genes = list(gene.keys())
                    mutant_gene = random.choice(genes)  #mutate single gene
                    mutant_trait = {mutant_gene: gene[mutant_gene]}
            if inherit:
                gene = inherit  #clonal division
                if random.random() > 0.9:   #crossover
                    group = self.matrix.species_group[self.species]
                    gene_xo = random.choice(group.sprites()).gene
                    gene_select = random.sample(range(1,len(gene)+1),
                                                len(gene)//2)
                    for gen in gene_select:
                        gene[gen] = gene_xo[gen]
                if mutation:    #clonal division with single mutation
                    gene[mutant_gene] = mutant_trait[mutant_gene]
            return gene

    def evolution(self, cycle=500, division_threshold=18):    #selection
        """
        Evolutionary selection.
        Arguments:
        cycle - rate of cell update;
        division_threshold - energy required for division.
        """
        if self.life:   #prosper or perish
            self.exist += 1
            self.ingest -= 1.0/cycle  #energy expenditure
            self.fitness = self.ingest/division_threshold * 100
            if self.exist > 100:
                self.exist = 0
                if self.fitness >= 100:   #replicate when reserves sufficient
                    self.ingest = division_threshold / 4
                    if self.species.count < self.species.maximum:
                        self.matrix.add_creature(
                            self.species, self.x, self.y, clone=True,
                            identity=self.identity,
                            inherit=self.gene.copy())     #give copy of self.gene, so that it's not modified
                elif self.fitness <= 0:   #possible decrease when reserves depleted
                    if random.random() > (0.9 - abs(self.fitness*0.1)):
                        self.life = False
                if self.species.count < self.species.minimum:  #fresh supply to gene pool, and stop extinction
                    self.matrix.add_creature(self.species)


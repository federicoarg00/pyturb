"""
"""
from pyturb.gas_models.perfect_ideal_gas import PerfectIdealGas
from pyturb.gas_models.semiperfect_ideal_gas import SemiperfectIdealGas
import numpy as np
import warnings

oxidizers = ['Air', 'O2', 'O3', 'O2(L)', 'O3(L)']
fuels = ['hydrocarbon', 'C8H18,isooctane', '']

class Combustion(object):
    """
    """

    def __init__(self, fuel, oxidizer):
        """
        """

        if not(isinstance(fuel, PerfectIdealGas) or isinstance(fuel, SemiperfectIdealGas) or isinstance(fuel, IdealLiquid)):
            # Check the flow is a Perfect or a Semiperfect gas fom pyturb
            raise TypeError("Object must be PerfectIdealGas, SemiperfectIdealGas or PerfectLiquid. Instead received {}".format(fluid))


        if not(isinstance(fuel, PerfectIdealGas) or isinstance(fuel, SemiperfectIdealGas) or isinstance(fuel, IdealLiquid)):
            # Check the flow is a Perfect or a Semiperfect gas from pyturb
            raise TypeError("Object must be PerfectIdealGas, SemiperfectIdealGas or PerfectLiquid. Instead received {}".format(fluid))

        
        self.oxidizer_list = oxidizers
        self.fuel_list = fuels


        self.fuel = fuel
        self.oxidizer = oxidizer


        reactants_status = self._classify_reactants()

        if not reactants_status:
            raise ValueError("Unknown fuel and oxidizer")


        return


    # Class properties for combustion thermodynamics
    @property
    def reactants(self):
        """
        Reactants of the combustion reaction.
        """
        return self._reactants


    @property
    def products(self):
        """
        Products of the combustion reaction.
        """
        return self._products


    @property
    def stoichiometric_reaction(self):
        """
        Stoichiometric reaction of the combustion reaction.
        """
        return self._stoichiometric_reaction


    @property
    def alpha(self):
        """
        Moles of carbon present in the fuel molecule, per mole of fuel.
        """
        return self._alpha

    
    @property
    def beta(self):
        """
        Moles of hydrogen present in the fuel molecule, per mole of fuel.
        """
        return self._beta


    @property
    def gamma(self):
        """
        Moles of oxygen present in the fuel molecule, per mole of fuel.
        """
        return self._gamma


    @property
    def delta(self):
        """
        Nytrogen present in the oxyder. 1 if true, 0 if false.
        """
        return self._delta


    @property
    def oxidizer_fuel_ratio(self):
        """
        Oxidizer to fuel stoichiometric molar ratio.
        """
        return self._oxidizer_fuel_ratio


    @property
    def stoich_far(self):
        """
        Stoichiometric fuel-air ratio.
        """
        return self._stoich_far


    def _classify_reactants(self):
        """
        """

        if not self.oxidizer.gas_species in self.oxidizer_list:
            warnings.warn("Requested oxidizer ({0}) not available. Available oxidizers: {1}".format(self.oxidizer.species, self.oxidizer_list))
            return False
    
        if not self.fuel.gas_species in self.fuel_list:
            warnings.warn("Requested fuel ({0}) not available. Available fuels: {1}".format(self.fuel.species, self.fuel_list))
            return False

        return True


    def stoichiometry(self):
        """
        """

        alpha = 0
        beta = 0
        gamma = 0
        reactants = ""
        productsC = ""
        productsH = ""


        for element in self.fuel.thermo_prop.chemical_formula:
            if element is "C":
                alpha = self.fuel.thermo_prop.chemical_formula[element]
                reactants += "C{0:1.0f}".format(alpha) if not alpha==0 else self.stoichiometric_reaction
                productsC += "{0:1.0f}CO2".format(alpha)
            
            elif element is "H":
                beta = self.fuel.thermo_prop.chemical_formula[element]
                reactants += "H{0:1.0f}".format(beta) if not beta==0 else self.stoichiometric_reaction
                productsH += "{0:1.0f}H2O".format(beta/2)
            
            elif element is "O":
                gamma = self.fuel.thermo_prop.chemical_formula[element]
                reactants += "O{0:1.0f}".format(gamma) if not gamma==0 else self.stoichiometric_reaction

        self._oxidizer_fuel_ratio = alpha + beta/4 - gamma/2

        if not (productsC is "" and productsH is ""):
            products = productsC + " + " + productsH

        elif productsC is "":
            products = productsH

        else:
            products = productsC

        if self.oxidizer.gas_species is "Air":
            delta = 1
            reactants += " + {0:1.3f}(O2 + 79/21 N2)".format(self.oxidizer_fuel_ratio)
            products += " + {0:1.3f}(79/21 N2)".format(self.oxidizer_fuel_ratio)

        else:
            delta = 0
            reactants += " + {0:1.3f} O2".format(self.oxidizer_fuel_ratio)

        self._stoichiometric_reaction = reactants + " --> " + products
        self._reactants = reactants
        self._products = products
        
        self._alpha = alpha
        self._beta = beta
        self._gamma = gamma
        self._delta = delta
        self._oxidizer_fuel_ratio = self.oxidizer_fuel_ratio

        if delta == 1:
            self._stoich_far = self.fuel.thermo_prop.Mg / (self.oxidizer_fuel_ratio/0.21*self.oxidizer.thermo_prop.Mg)
        
        else:
            self._stoich_far = np.nan

        
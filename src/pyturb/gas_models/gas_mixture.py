"""
gas_mixture:
------------

Gas mixture of ideal gases. The approach for the ideal gases may be Perfect or Semiperfect.

MRodriguez 2020

"""
import pyturb.utils.constants as cts
from pyturb.gas_models.gas import Gas
from pyturb.gas_models.perfect_ideal_gas import PerfectIdealGas
from pyturb.gas_models.semiperfect_ideal_gas import SemiperfectIdealGas
import numpy as np
import pandas as pd
import warnings


class GasMixture(object):
    """
    GasMixture:
    -----------



    """

    def __init__(self, gas_model = "perfect", mixture=None):
        """
        """
        # Gas model selector:
        if gas_model.lower() == "perfect":
            self.gas_model = PerfectIdealGas
        elif gas_model.lower() == "semi-perfect" or gas_model.lower() == "semiperfect":
            self.gas_model = SemiperfectIdealGas
        else:
            self.gas_model = None
            raise ValueError("gas_model may be 'perfect' or 'semi-perfect', instead received {}".format(gas_model))

        self._n_species = 0
        self._gas_species = "mixture"
        self._mixture_gases_columns = ['gas_species', 'gas_properties', 'Ng', 'Mg', 'mg', 'Rg', 'molar_frac', 'mass_frac']
        self._mixture_gases = pd.DataFrame(columns=self._mixture_gases_columns)


        # Mixture initialization:
        if not mixture is None:
            if not type(mixture) is dict:
                warnings.warn("mixture must be a dictionary with keys:=species and value:=moles. Instead received {}".format(mixture))
            else:
                #TODO: call add_gas for each pure substance in the mixture
                print("")

        return


    @property
    def gas_species(self):
        """
        Gets the Name of the gas species selected. May be a pure substance or any of the 
        molecules and mixes considered in "NASA Glenn Coefficients for Calculating Thermodynamic
        Properties of Individual Species".
        """
        
        return self._gas_species


    @property
    def n_species(self):
        """
        Number of different gas species in the gas mixture
        """
        return self._n_species


    @property
    def mixture_gases(self):
        """
        Dataframe with the thermodynamic properties of the gas species in the mixture.
        """
        return self._mixture_gases
    
    
    @property
    def Ng(self):
        """
        Moles of the mixture. [mol]
        """
        return self._Ng
    

    @property
    def mg(self):
        """
        Mass quantity of the mixture. [kg]
        """
        return self._mg
    

    @property
    def Ru(self):
        """
        Get the Ideal Gas Law constant Ru [J/mol/K]
        """
        
        Ru = cts.Ru
        return Ru

    
    @property
    def Rg(self):
        """
        Get the Mixture Gas constant Rg =  Ru/Mg [J/kg/K]
        """
        
        Rg = self.Ru/self.Mg*1e3
        return Rg


    @property
    def Mg(self):
        """
        Get the Mixture molecular mass [g/mol]
        """
        return self._Mg


    def add_gas(self, species, moles=None, mass=None):
        """
        add_gas:
        --------

        Adds a gas species to the mixture. The amount of gas must be specified
        in moles or kilograms.

        - species: string. Gas species.
        - moles: float. Number of moles of the selected gas. If None, then mass must be provided
        - mass: float. Mass quantity of the selected gas. If none, then moles must be provided

        """

        if moles is None and mass is None:
            raise ValueError('Quantity (moles or mass) of gas must be specified in add_gas.')
        else:

            pure_substance = self.gas_model(species)

            if mass is None:
                moles_ = moles # mol
                mass_ = moles_ * pure_substance.Rg * 1e-3 # kg

            elif moles is None:
                mass_ = mass #kg
                moles_ = mass_ / pure_substance.Rg * 1e3 # mol

            else:
                warnings.warn("mass ({0}kg) will be dismised and recalculated with the moles quantity provided: {1}mol.".format(mass, moles))
                moles_ = moles
                mass_ = mass_ = moles_ * pure_substance.Rg * 1e3 # kg


        subst_props = {'gas_species': pure_substance.gas_species, 'gas_properties': pure_substance, 'Ng': moles_, 'Mg': pure_substance.thermo_prop.Mg, 'mg': mass_, 'Rg': pure_substance.Rg, 'molar_frac': np.nan, 'mass_frac': np.nan}

        new_gas = len(self._mixture_gases.index)
        self._mixture_gases.loc[new_gas] = subst_props

        self._update_mixture_properties()

        return


    def _update_mixture_properties(self):
        """
        Updates mixture properties of the gas mixture
        """

        self._n_species = len(self.mixture_gases.index)

        self._Ng = np.sum(self.mixture_gases['Ng'])
        self._mg = np.sum(self.mixture_gases['mg'])

        self._mixture_gases['molar_frac'] = self.mixture_gases['Ng'] / self.Ng
        self._mixture_gases['mass_frac'] = self.mixture_gases['mg'] / self.mg

        self._Mg = 0
        for ii, xi in enumerate(self.mixture_gases['molar_frac']):
            self._Mg += xi * self.mixture_gases.loc[ii]['Mg']


        return


    def cp_molar(self, temperature=None):
        """
        Molar heat capacity ratio at constant pressure [J/mol/K].

        As a semiperfect gas, cp is a function of the temperature. It is calculated as a
        7 coefficients polynomial:
            cp/Rg = a1*T**(-2) + a2*T**(-1) + a3 + a4*T**(1) + a5*T**(2) + a6*T**(3) + a7*T**(4)

        As a perfect gas, cp is considered invariant with temperature. It is calculated as a
        semi-perfect gas (which means cp(T)) at T_ref temperature for any temperature.
        """

        if temperature is None:
            if not(isinstance(self.gas_model, SemiperfectIdealGas)):
                raise ValueError("If gas model is semi-perfect a temperature must be provided to calculate the cp.")

        cp_ = 0
        for ii, xi in enumerate(self.mixture_gases['molar_frac']):
            cp_ += xi * self.mixture_gases.loc[ii]['gas_properties'].cp_molar(temperature)

        return cp_


    def cp(self, temperature=None):
        """
        Heat capacity ratio at constant pressure [J/kg/K].

        As a semiperfect gas, cp is a function of the temperature. It is calculated as a
        7 coefficients polynomial:
            cp/Rg = a1*T**(-2) + a2*T**(-1) + a3 + a4*T**(1) + a5*T**(2) + a6*T**(3) + a7*T**(4)

        As a perfect gas, cp is considered invariant with temperature. It is calculated as a
        semi-perfect gas (which means cp(T)) at T_ref temperature for any temperature.
        """

        cp_ = self.cp_molar(temperature)
        cp_ *= 1e3/self.Mg

        return cp_


    def cv_molar(self, temperature=None):
        """
        Molar heat capacity ratio at constant volume [J/mol/K].

        As a semiperfect gas, cp is a function of the temperature. It is calculated as a
        7 coefficients polynomial:
            cp/Rg = a1*T**(-2) + a2*T**(-1) + a3 + a4*T**(1) + a5*T**(2) + a6*T**(3) + a7*T**(4)

        As a semiperfect gas, cv is a function of tempeature. cv is calculated with the 
        Mayer equation: cv(T) = cp(T) - Rg (ideal gas).
        """

        cv_ = self.cp_molar(temperature) - self.Ru

        return cv_


    def cv(self, temperature=None):
        """
        Heat capacity ratio at constant volume [J/kg/K]

        As an ideal gas, cv is invariant with tempeature. cv is calculated with the 
        Mayer equation: cv = cp - Rg.
        """
        
        cv_ = self.cp(temperature) - self.Rg

        return cv_


    def gamma(self, temperature=None):
        """
        Heat capacity ratio cp/cv [-].

        As a perfect gas, gamma is considered invariant with temperature. gamma is calculated
        as gamma = cp/cv.

        As a semiperfect gas, gamma is a function of tempeature. Gamma is calculated with the 
        Mayer equation: cv(T) = cp(T) - Rg (ideal gas).
        """

        gamma_ = self.cp_molar(temperature) / self.cv_molar(temperature)

        return gamma_

    
    def h0_molar(self, temperature):
        """
        assigned molar enthalpy:
            h0(T) = deltaHf(T_ref) + (h0(T) - h0(T_ref)) [J/mol].

        """

        if temperature is None:
            if not(isinstance(self.gas_model, SemiperfectIdealGas)):
                raise ValueError("If gas model is semi-perfect a temperature must be provided to calculate the cp.")

        h0_ = 0
        for ii, xi in enumerate(self.mixture_gases['molar_frac']):
            h0_ += xi * self.mixture_gases.loc[ii]['gas_properties'].h0_molar(temperature)

        return h0_
            

    def h0(self, temperature):
        """
        assigned enthalpy:
            h0(T) = deltaHf(T_ref) + (h0(T) - h0(T_ref)) [J/kg].

        """

        if temperature is None:
            if not(isinstance(self.gas_model, SemiperfectIdealGas)):
                raise ValueError("If gas model is semi-perfect a temperature must be provided to calculate the cp.")

        h0_ = self.h0_molar(temperature) * 1e3/self.Mg

        return h0_
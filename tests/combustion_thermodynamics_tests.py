from pyturb.combustion.combustion_thermodynamics import Combustion
from pyturb.gas_models.perfect_ideal_gas import PerfectIdealGas

air = PerfectIdealGas('Air')
fuel = PerfectIdealGas('C8H18,isooctane')

comb = Combustion(fuel, air)

comb.stoichiometry()
print(comb.stoichiometric_reaction)

print(comb.stoich_far)
print(comb.alpha)
print(comb.beta)
print(comb.gamma)
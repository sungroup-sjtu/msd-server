import os
import shutil

from ..simulation import Simulation
from ...errors import GmxError
from ...jobmanager import Local
from ...wrapper import GMX


class GmxSimulation(Simulation):
    def __init__(self, packmol_bin=None, dff_root=None, gmx_bin=None, jobmanager=Local()):
        super().__init__(packmol_bin=packmol_bin, dff_root=dff_root, jobmanager=jobmanager)
        self.gmx = GMX(gmx_bin=gmx_bin)

    def export(self, ff='TEAM_LS', gro_out='conf.gro', top_out='topol.top', mdp_out='grompp.mdp', minimize=False):
        print('Checkout force field: %s ...' % ff)
        self.dff.checkout(self.msd, table=ff)
        print('Export GROMACS files ...')
        self.dff.export_gmx(self.msd, ff + '.ppf', gro_out, top_out, mdp_out)

        if minimize:
            print('Energy minimize ...')
            self.gmx.minimize(gro_out, top_out, name='em', silent=True)

            if os.path.exists('em.gro'):
                shutil.move('em.gro', gro_out)
            else:
                raise GmxError('Energy minimization failed')

    def check_finished(self, log=None):
        if log == None:
            log = self.procedure + '.log'
        if not os.path.exists(log):
            return False
        with open(log) as f:
            lines = f.readlines()
        try:
            last_line = lines[-1]
        except:
            return False
        if last_line.startswith('Finished mdrun'):
            return True
        else:
            return False

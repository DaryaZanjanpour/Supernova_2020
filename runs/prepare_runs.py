#!/usr/bin/env python
import os, sys
sys.path.append('../')

import matplotlib.pyplot as plt
import numpy as np
import astropy.units as u

import imagine as img
import imagine_snrs as img_snrs
from imagine.fields import FieldFactory
from imagine.priors import FlatPrior, GaussianPrior

# ----------------- Measurements, simulator and likelihood -------------------

measurements = img.observables.Measurements(img_snrs.datasets.SNR_DA530_I(),
                                            img_snrs.datasets.SNR_DA530_Q(),
                                            img_snrs.datasets.SNR_DA530_U())

simulator = img_snrs.simulators.SimpleSynchrotron(measurements,
                                                  distance=11.3*u.kpc,
                                                  gamma=3.,
                                                  beam_kernel_sd=2.5)

likelihood = img.likelihoods.SimpleLikelihood(measurements)

L = 70*u.pc; N = 200
grid = img.fields.UniformGrid(box=[[-L,L],[-L,L],[-L,L]],
                              resolution=[N, N, N])

# ----------------- Field factories --------------------------

te_factory = FieldFactory(grid=grid,
                          field_class=img_snrs.fields.SNRThermalElectrons,
                          active_parameters=(),
                          default_parameters={'initial_electron_density': 0.01*u.cm**-3,
                                              'shell_V0':0.0153*u.pc/u.yr,
                                              'shell_a': 1.3,
                                              'shell_b': 10,
                                              'elapsed_time': 1300*u.yr,
                                              'shell_radius': 35*u.pc},
                          priors={'initial_electron_density': FlatPrior(1e-4, 10, u.cm**-3),
                                  'shell_V0': FlatPrior(1e-3, 0.1, u.pc/u.yr),
                                  'shell_a': FlatPrior(0.5, 2),
                                  'shell_b': FlatPrior(1, 50),
                                  'elapsed_time': FlatPrior(500, 3000, u.yr),
                                  'shell_radius': FlatPrior(10, 200, u.pc)})

B_uniform_factory  = FieldFactory(grid=grid,
                                  field_class=img_snrs.fields.SNRUniformMagneticField,
                                  active_parameters =('B', 'beta', 'gamma'),
                                  default_parameters={},
                                    priors={'B': FlatPrior(0, 10, u.microgauss),
                                            'beta': FlatPrior(-90, 90, u.deg),
                                            'gamma': FlatPrior(-180, 180, u.deg, wrapped=True)})

B_helical_factory  = FieldFactory(grid=grid,
                                  field_class=img_snrs.fields.SNRSimpleHelicalMagneticField,
                                  active_parameters =('B', 'alpha', 'beta', 'gamma', 'period'),
                                  default_parameters={},
                                    priors={'B': FlatPrior(0, 10, u.microgauss),
                                            'alpha': FlatPrior(-180, 180, u.deg, wrapped=True),
                                            'beta': FlatPrior(-90, 90, u.deg),
                                            'gamma': FlatPrior(-180, 180, u.deg, wrapped=True),
                                            'period': FlatPrior(10,70, u.pc)})

B_BMF_factory = FieldFactory(grid=grid,
                             field_class=img_snrs.fields.SNR_BMF_MagneticField,
                             active_parameters=['B', 'period',
                                                'x_shift', 'y_shift',
                                                'alpha', 'beta'],
                             default_parameters={'B': 1*u.microgauss},
                             priors={'B': FlatPrior(0, 10, u.microgauss),
                                     'alpha': FlatPrior(-180, 180, u.deg, wrapped=True),
                                     'beta': FlatPrior(-90, 90, u.deg),
                                     'x_shift': FlatPrior(-L,L),
                                     'y_shift': FlatPrior(-L,L),
                                     'period': FlatPrior(10,120, u.pc)})

B_CK_m0_factory = FieldFactory(grid=grid,
                               field_class=img_snrs.fields.SNR_CK_MagneticField,
                               active_parameters=['B', 'period', 'period_z',
                                                  'x_shift', 'y_shift',
                                                  'alpha', 'beta', 'gamma'],
                               default_parameters={'B': 1*u.microgauss,
                                                   'm': 0,
                                                   'z_shift': 0*u.pc},
                                   priors={'B': FlatPrior(0, 10, u.microgauss),
                                           'alpha': FlatPrior(-180, 180, u.deg, wrapped=True),
                                           'beta': FlatPrior(-90, 90, u.deg),
                                           'gamma': FlatPrior(-180, 180, u.deg, wrapped=True),
                                           'x_shift': FlatPrior(-L,L),
                                           'y_shift': FlatPrior(-L,L),
                                           'period': FlatPrior(10,120, u.pc),
                                           'period_z': FlatPrior(10,220, u.pc)})

B_CK_m1_factory = FieldFactory(grid=grid,
                               field_class=img_snrs.fields.SNR_CK_MagneticField,
                               active_parameters=['B', 'period', 'period_z',
                                                  'x_shift', 'y_shift',
                                                  'alpha', 'beta', 'gamma'],
                               default_parameters={'B': 1*u.microgauss,
                                                   'm': 1,
                                                   'z_shift': 0*u.pc},
                                   priors={'B': FlatPrior(0, 10, u.microgauss),
                                           'alpha': FlatPrior(-180, 180, u.deg, wrapped=True),
                                           'beta': FlatPrior(-90, 90, u.deg),
                                           'gamma': FlatPrior(-180, 180, u.deg, wrapped=True),
                                           'x_shift': FlatPrior(-L,L),
                                           'y_shift': FlatPrior(-L,L),
                                           'period': FlatPrior(10,120, u.pc),
                                           'period_z': FlatPrior(10,220, u.pc)})

CR_factory = FieldFactory(grid=grid,
                          field_class=img_snrs.fields.EquipartitionCosmicRayElectrons,
                          active_parameters=(),
                          default_parameters={'cr_energy': 1*u.GeV,
                                              'Ecr_Em': 1},
                          priors={'Ecr_Em': GaussianPrior(mu=1, sigma=0.1,
                                                          xmin=1e-2, xmax=10)})

# ----------------- Pipelines --------------------------

Pipeline = img.pipelines.UltranestPipeline

pipeline_uniform = Pipeline(run_directory='uniform_field',
                            simulator=simulator, likelihood=likelihood,
                            factory_list=[B_uniform_factory, CR_factory, te_factory])
pipeline_uniform.name = 'Uniform initial magnetic field'

pipeline_simple_helical = Pipeline(run_directory='simple_helical_field',
                                   simulator=simulator, likelihood=likelihood,
                                   factory_list=[B_helical_factory, CR_factory, te_factory])
pipeline_simple_helical.name = 'Simple helical initial magnetic field'

pipeline_BMF = Pipeline(run_directory='BMF_field',
                              simulator=simulator, likelihood=likelihood,
                              factory_list=[B_BMF_factory, CR_factory, te_factory])
pipeline_BMF.name = 'BMF initial magnetic field'

pipeline_CK_m0 = Pipeline(run_directory='CK_m0_field',
                          simulator=simulator, likelihood=likelihood,
                          factory_list=[B_CK_m0_factory, CR_factory, te_factory])
pipeline_CK_m0.name = 'CK (m=0) initial magnetic field'

pipeline_CK_m1 = Pipeline(run_directory='CK_m1_field',
                          simulator=simulator, likelihood=likelihood,
                          factory_list=[B_CK_m1_factory, CR_factory, te_factory])
pipeline_CK_m1.name = 'CK (m=1) initial magnetic field'


pipelines = [pipeline_simple_helical, pipeline_uniform, pipeline_BMF,
             pipeline_CK_m0, pipeline_CK_m1]

for p in pipelines:
    p.likelihood_rescaler = 1e-9
    p.sampling_controllers={'min_num_live_points':200}
    print('\nTesting', p.name, '\n')
    p.test(n_points=2)
    print('\nSaving', p.name)
    p.save()


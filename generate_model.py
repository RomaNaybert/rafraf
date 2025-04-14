import torch
from smplx import SMPLX
import trimesh
import matplotlib.pyplot as plt
import os
import numpy as np


class SMPLBetasCalculator:
    def __init__(self):
        self._initialized = False
        self._numberOfBetas = 10
        self._betas = np.zeros(self._numberOfBetas)

        self._female_a = -2.35648430867
        self._female_b = 1001.43505432

        self._female_A = np.array([
            [12.5455942127, 5.0553042489],
            [10.1758392683, -37.1027483933],
            [1.24469952215, 4.75375379164],
            [-0.542029599023, 3.37980447348],
            [1.45700314783, -4.13427384673],
            [-1.36463259494, 6.33289691775],
            [0.925913696254, -3.13680061231],
            [0.457392221203, 0.216023467283],
            [0.0559419015304, 0.0270701274621],
            [-0.0557684951813, -0.396172003207]
        ])

        self._female_B = np.array([
            [-22.729500163],
            [-1.56447178772],
            [-3.99625051267],
            [-0.491353884744],
            [-0.706445124292],
            [-0.345945415946],
            [-0.240311855035],
            [-0.841667628854],
            [-0.103206961499],
            [0.254059051018]
        ])

        self._female_A4 = np.array([
            [5.63579016713, 7.60890528036, 0.452722432905, 2.4197141873],
            [-4.35780123887, 10.6876401936, 4.80511344637, -33.213203264],
            [-26.0670648506, 33.3754948041, -16.5940549239, 11.7360074219],
            [-20.8935617795, -29.1869472507, 71.5400886278, 39.4489608787],
            [-2.58651976071, 1.74608175362, 2.87493426825, -1.81745028738],
            [-2.00158048136, -2.58800926954, 4.48164889916, 8.93638690243],
            [-2.03179406026, 1.81687669728, 1.22295621831, -1.68875003894],
            [-5.78484854238, -3.85705329802, 14.1670850974, 8.17668953384],
            [-2.41554163399, -1.03303211433, 4.80431049637, 2.95198573595],
            [-5.20121168337, -3.44146349041, 11.9681495406, 6.4849131455]
        ])        

        self._female_B4 = np.array([
            [-23.2814628892],
            [-0.397156802718],
            [-3.52614327241],
            [12.0724303702],
            [-0.0103075197805],
            [0.516951398438],
            [0.157796584873],
            [1.82668124406],
            [0.85135827304],
            [2.5426457183]
        ])

        self._female_A5 = np.array([
            [5.58315242701, 7.57770596161, 0.591752635088, -0.395458388155, 2.8180693875],
            [-2.76902362522, 11.6293367613, 0.608731300312, 11.9362159697, -45.2368544108],
            [-25.9007989979, 33.4740435131, -17.033207043, 1.24912707058, 10.4777302449],
            [-21.5947041037, -29.6025266964, 73.3919910626, -5.26756302161, 44.7551098565],
            [-5.8718796399, -0.201209103868, 11.5524391764, -24.6823499522, 23.0457028309],
            [1.60413500383, -0.45083798322, -5.04199994627, 27.0891271296, -18.351173519],
            [-10.032797905, -2.92545967086, 22.3557248299, -60.1101809621, 58.8617500603],
            [-3.79006860009, -2.67471197555, 8.89834335328, 14.9864424062, -6.91953157014],
            [-1.48611004729, -0.48214158848, 2.34943570273, 6.98266142014, -4.08182508021],
            [-3.7995513317, -2.61067463059, 8.26599360381, 10.5304358081, -4.12266021788]
        ])

# Female_B5 matrix (10x1)
        self._female_B5 = np.array([
            [-23.2576329316],
            [-1.11642216453],
            [-3.60141451722],
            [12.389848858],
            [1.47702811606],
            [-1.11541440958],
            [3.77998063116],
            [0.923612051359],
            [0.430589538164],
            [1.90809137203]
        ])

# Female_A6 matrix (10x6)
        self._female_A6 = np.array([
            [14.4918254166, 6.61300190847, 1.20421205709, 7.45243288031, -31.3425042765, -4.18787735526],
            [-14.9668401678, 12.9502162089, 9.7459361556, -8.78495944203, 42.914373173, -35.6442637774],
            [-28.7752479493, 33.7853123808, 0.732981620027, -19.2468560522, 10.1128898388, 12.7382505595],
            [-36.8376937116, -27.9518909762, -8.00464406627, 61.6531745404, 53.6279047992, 56.7424814345],
            [-50.919948287, 4.67696461073, -32.7713284245, -23.139640667, 158.488170558, 58.4723449554],
            [-69.7713082422, 7.27827941442, 14.2727192077, -60.0091195212, 251.113172275, 37.7798074596],
            [2.21761388414, -4.25203456247, -57.9104569736, 31.7899198279, -43.0994138339, 49.2277975433],
            [-87.0557115662, 6.34197360153, 0.0349913525243, -55.2255674101, 292.945287565, 58.5621244301],
            [96.1277455855, -11.0525691124, 24.5105244458, 77.5230840995, -343.425187028, -80.8471833686],
            [189.06366582, -23.495482896, 45.1615855666, 156.792363973, -678.531607955, -155.793894484]
        ])

# Female_B6 matrix (10x1)
        self._female_B6 = np.array([
            [-23.4792301165],
            [-1.37387410553],
            [-4.03716236852],
            [12.666773328],
            [1.54113120149],
            [-1.23832147038],
            [3.99857384669],
            [1.20682627202],
            [0.530951734617],
            [2.07392894341]
        ])

        self._male_a = -5.28069181198
        self._male_b = 1056.44071546

# Матрица _male_A (10x2)
        self._male_A = np.array([
            [-11.5400924739, -6.0210667838],
            [11.4194637569, -45.3828342674],
            [1.33640697715, 3.67473124984],
            [0.00459803156834, -1.23588204264],
            [-1.81353876182, 5.68304846595],
            [-1.99482266027, 10.0631255165],
            [0.570609492393, -2.82022832303],
            [0.18967538558, 0.929038237599],
            [-0.273559389343, 0.0622436919832],
            [0.93626464489, -4.06420392784]
        ])

# Матрица _male_B (10x1)
        self._male_B = np.array([
            [23.2009238013],
            [-0.576973330703],
            [-3.98478070278],
            [0.530568503305],
            [0.756108703384],
            [-0.830098157171],
            [0.212038910783],
            [-0.743195634399],
            [0.460625196094],
            [0.102366707097]
        ])

# Матрица _male_A4 (10x4)
        self._male_A4 = np.array([
            [-5.31800336209, -7.29693684696, 0.011406720731, -2.92597394432],
            [-4.45172837311, 8.31978771786, 9.51223184463, -34.4713369665],
            [-24.9197778087, 33.0885553309, -16.9029024293, 3.33107591018],
            [15.8644149399, 22.6844797261, -50.5184675747, -54.6733479749],
            [-1.2524152942, -6.47159517372, 8.08488540688, 13.4887562698],
            [-12.2062633482, -18.4848578216, 37.4978321452, 49.9774985649],
            [3.29686016729, 5.80396751821, -11.2415727263, -14.575974303],
            [-3.75430694444, -3.90648104224, 10.1393555515, 11.9850556095],
            [1.90171527577, -0.141388152957, -2.36062141437, -3.10795574204],
            [-5.17429447819, -1.25727902176, 9.04289703015, 6.8555207938]
        ])

# Матрица _male_B4 (10x1)
        self._male_B4 = np.array([
            [24.0480529161],
            [0.613658470929],
            [-0.874364015716],
            [-4.55456489319],
            [1.36513213964],
            [3.01296084015],
            [-0.88237888489],
            [0.368192515012],
            [0.0382875861558],
            [1.38423991302]
        ])

# Матрица _male_A5 (10x5)
        self._male_A5 = np.array([
            [-5.1984090408, -7.11780118166, -0.516086205831, 1.98602830178, -4.50463008388],
            [-3.35252437671, 9.96624247484, 4.66398882864, 18.2537951862, -48.9809317266],
            [-24.7009186792, 33.4163758774, -17.8682211958, 3.63445705898, 0.44211509075],
            [18.7482576003, 27.0040750715, -63.2381902859, 47.8901763856, -92.7403387161],
            [-0.485303285807, -5.32256804181, 4.70139567307, 12.7389506698, 3.36280656994],
            [-9.62972558114, -14.6255624797, 26.1335346396, 42.7869556906, 15.9669609339],
            [-0.892707037613, -0.471421651411, 7.23729016697, -69.5735295065, 40.7267015993],
            [-1.78983365367, -0.963973186434, 1.47468189383, 32.6227826826, -13.9461741344],
            [4.75350477523, 4.13019601402, -14.9389677169, 47.3578895345, -40.7518417849],
            [-7.65646164671, -4.97522032803, 19.9909555149, -41.2198020208, 39.6203577667]
        ])

# Матрица _male_B5 (10x1)
        self._male_B5 = np.array([
            [23.8953831199],
            [-0.789545697272],
            [-1.15375168509],
            [-8.23597439925],
            [0.385864623157],
            [-0.27615432506],
            [4.46587147095],
            [-2.13958321993],
            [-3.60220401102],
            [4.55288497658]
        ])

# Матрица _male_A6 (10x6)
        self._male_A6 = np.array([
            [-6.11197136111, -7.10983720445, 2.28878763516, -1.06975095489, 3.09285984449, -4.08191180573],
            [-10.7915639858, 10.0310922838, 20.7191318392, 0.155556391356, 25.1848246986, -45.5387823027],
            [-29.7651304247, 33.4605231305, 5.31276333112, -20.9373884139, 17.1448589803, 2.78539788778],
            [30.3342029028, 26.9030746227, 44.0505334862, -56.2165242694, -39.224149453, -98.1013203811],
            [-10.1578871538, -5.23824731648, 15.9444955777, -1.16067700759, 32.746475607, 7.83844868758],
            [-29.0623577253, -14.4561585583, 49.227031669, 14.3563814445, 65.7890614518, 24.9587161948],
            [-75.1645605536, 0.176043043207, -44.9594486061, -37.7751914389, 251.446921799, 75.0933445034],
            [-11.879702557, -0.876014779865, 35.9666180348, -4.64028652174, 34.1591916317, -9.27744829631],
            [-31.2442974897, 4.44400676395, 59.2877495722, -36.755447791, 121.870347144, -24.095146722],
            [54.948602037, -5.52097981188, -61.9674477215, 57.93277525, -211.949073668, 10.6521044412]
        ])

# Матрица _male_B6 (10x1)
        self._male_B6 = np.array([
            [24.0520893565],
            [0.486496314768],
            [-0.285071413889],
            [-10.2233482717],
            [2.04503355209],
            [3.05718657962],
            [17.2059576083],
            [-0.408836067981],
            [2.57261296066],
            [-6.18595977018]
        ])

        self._vRoot_h = np.zeros((2, 1))
        self._vRoot_h4 = np.zeros((4, 1))
        self._vRoot_h5 = np.zeros((5, 1))
        self._vRoot_h6 = np.zeros((6, 1))
        self._betasMatrix = np.zeros((10, 1))

    def initialize(self):
        self._initialized = True
        return True

    def _betaFromHeightWeight(self, height, weight, a, b, A, B):
        num = ((weight - a) / b) ** (1.0 / 3.0)
        self._vRoot_h[0, 0] = height
        self._vRoot_h[1, 0] = num
        self._betasMatrix = np.dot(A, self._vRoot_h) + B
        self._betas = self._betasMatrix.flatten()


    def _betaFromHeightWeightArmspanInseam(self, height, weight, armspan, inseam, a, b, A, B):
        num = ((weight - a) / b) ** (1.0 / 3.0)
        self._vRoot_h4[0, 0] = armspan
        self._vRoot_h4[1, 0] = height
        self._vRoot_h4[2, 0] = inseam
        self._vRoot_h4[3, 0] = num
        self._betasMatrix = np.dot(A, self._vRoot_h4) + B
        self._betas = self._betasMatrix.flatten()

    def _betaFromRegressor5(self, height, weight, armspan, inseam, inseamWidth, a, b, A, B):
        num = ((weight - a) / b) ** (1.0 / 3.0)
        self._vRoot_h5[0, 0] = armspan
        self._vRoot_h5[1, 0] = height
        self._vRoot_h5[2, 0] = inseam
        self._vRoot_h5[3, 0] = inseamWidth
        self._vRoot_h5[4, 0] = num
        self._betasMatrix = np.dot(A, self._vRoot_h5) + B
        self._betas = self._betasMatrix.flatten()

    def _betaFromRegressor6(self, height, weight, armspan, inseam, inseamWidth, wristToShoulder, a, b, A, B):
        num = ((weight - a) / b) ** (1.0 / 3.0)
        self._vRoot_h6[0, 0] = armspan
        self._vRoot_h6[1, 0] = height
        self._vRoot_h6[2, 0] = inseamWidth
        self._vRoot_h6[3, 0] = inseam
        self._vRoot_h6[4, 0] = wristToShoulder
        self._vRoot_h6[5, 0] = num
        self._betasMatrix = np.dot(A, self._vRoot_h6) + B
        self._betas = self._betasMatrix.flatten()

    def calculateBetas(self, measurements, gender):
        if not self._initialized:
            return False
        height = measurements[0]
        weight = measurements[1]
        print(height, weight)
        if gender == 'female':
            if len(measurements) == 2:
                self._betaFromHeightWeight(height, weight, self._female_a, self._female_b, self._female_A, self._female_B)
            elif len(measurements) == 4:
                armspan = measurements[2]
                inseam = measurements[3]
                self._betaFromHeightWeightArmspanInseam(height, weight, armspan, inseam, self._female_a, self._female_b, self._female_A4, self._female_B4)
            elif len(measurements) == 5:
                armspan = measurements[2]
                inseam = measurements[3]
                inseamWidth = measurements[4]
                self._betaFromRegressor5(height, weight, armspan, inseam, inseamWidth, self._female_a, self._female_b, self._female_A5, self._female_B5)
            else:
                armspan = measurements[2]
                inseam = measurements[3]
                inseamWidth = measurements[4]
                wristToShoulder = measurements[5]
                self._betaFromRegressor6(height, weight, armspan, inseam, inseamWidth, wristToShoulder, self._female_a, self._female_b, self._female_A6, self._female_B6)
        else:
            if len(measurements) == 2:
                self._betaFromHeightWeight(height, weight, self._male_a, self._male_b, self._male_A, self._male_B)
            elif len(measurements) == 4:
                armspan = measurements[2]
                inseam = measurements[3]
                self._betaFromHeightWeightArmspanInseam(height, weight, armspan, inseam, self._male_a, self._male_b, self._male_A4, self._male_B4)
            elif len(measurements) == 5:
                armspan = measurements[2]
                inseam = measurements[3]
                inseamWidth = measurements[4]
                self._betaFromRegressor5(height, weight, armspan, inseam, inseamWidth, self._male_a, self._male_b, self._male_A5, self._male_B5)
            else:
                armspan = measurements[2]
                inseam = measurements[3]
                inseamWidth = measurements[4]
                wristToShoulder = measurements[5]
                self._betaFromRegressor6(height, weight, armspan, inseam, inseamWidth, wristToShoulder, self._male_a, self._male_b, self._male_A6, self._male_B6)
        return True

    def calculateWeight(self, volume, gender):
        if gender == 'female':
            return volume * self._female_b + self._female_a
        else:
            return volume * self._male_b + self._male_a

    def getBetas(self):
        return self._betas
    

class GenerateAvarar:
    def __init__(self, height: float, weight: float, armspan: float, inseam: float, gender: str):
        models = {
            'male': 'models/SMPLX_MALE.npz',
            'female': 'models/SMPLX_FEMALE.npz'
        }
        
        calculator = SMPLBetasCalculator()
        calculator.initialize()

        fweight = lambda x: 281 + ((x - 1) * (-2.74))
        print(height, fweight(weight), armspan, inseam)
        measurements = [height, fweight(weight), armspan, inseam]
        calculator.calculateBetas(measurements, gender)

        self.shape_params = torch.tensor(
            calculator.getBetas()
            , dtype=torch.float
        ).view(1, -1)

        self.model = models[gender]
        self.gender = gender

    def generate_avatar(self, filename='mesh'):
        smplx_model = SMPLX(model_path=self.model, gender=self.gender, batch_size=1, use_pca=False)

        global_orient = torch.zeros(1, 3)  # Вектор глобальной ориентации тела
        body_pose = torch.zeros(1, 63)     # Вектор позы для тела (21 сустав)
        left_hand_pose = torch.zeros(1, 45)  # Вектор позы для левой руки (15 суставов)
        right_hand_pose = torch.zeros(1, 45)  # Вектор позы для правой руки (15 суставов)
        jaw_pose = torch.zeros(1, 3)  # Вектор позы для челюсти
        leye_pose = torch.zeros(1, 3)  # Вектор позы для левого глаза
        reye_pose = torch.zeros(1, 3)  # Вектор позы для правого глаза

        output = smplx_model.forward(
            betas=self.shape_params
        )

        vertices = output.vertices.detach().cpu().numpy().squeeze()
        joints = smplx_model.faces

        mesh = trimesh.Trimesh(vertices=vertices,
            faces=joints,
            process=False,
            maintain_order=True)
        mesh_fname = f'styles/models/{filename}.obj'

        if os.path.exists(mesh_fname):
            os.remove(mesh_fname)

        mesh.export(mesh_fname)

        return mesh_fname
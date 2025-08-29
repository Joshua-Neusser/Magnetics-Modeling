import numpy as np

class LeakageInductanceCalculator:

    def __init__(self,
                 SelectedCore, 
                 ReferredWinding,
                 WindowWidth, WindowHeight,
                 EquivalentWindingsBlocks,
                 NumberOfTurns_1, NumberOfTurns_2):


        self.LeakageInductance = self._LeakageScaler(
                 SelectedCore, 
                 ReferredWinding,
                 WindowWidth, WindowHeight,
                 EquivalentWindingsBlocks,
                 NumberOfTurns_1, NumberOfTurns_2)



    # 2D Leakage Functions
    @staticmethod
    def Leakage_pul_IW_calc_vectorized(M, N, I_ref, WindowWidth, WindowHeight,
                                    NumberOfTurns_1, I_1, Width_1, Height_1, NumberOfTurns_2, I_2, Width_2, Height_2,
                                    Height_1_Minus, Height_1_Plus, Height_2_Minus, Height_2_Plus,
                                    Width_1_Minus, Width_1_Plus, Width_2_Minus, Width_2_Plus):

        mu_0 = 4 * np.pi * 1e-7  # Vacuum Permeability
        J_1 = (NumberOfTurns_1 * I_1) / (Width_1 * Height_1) # Current Density
        J_2 = (NumberOfTurns_2 * I_2) / (Width_2 * Height_2) # Current Density

        ### Somatório em m (vetorizado)
        m_vec = np.arange(1, M, dtype=np.float64)
        
        J1_m0 = ((2 * J_1) / (m_vec * WindowHeight * np.pi)) * (np.sin((m_vec * np.pi * Width_1_Plus) / WindowWidth) - np.sin((m_vec * np.pi * Width_1_Minus) / WindowWidth)) * (Height_1_Plus - Height_1_Minus)
        A1_m0 = (mu_0 * J1_m0) / (((m_vec * np.pi) / WindowWidth)**2)
        J2_m0 = ((2 * J_2) / (m_vec * WindowHeight * np.pi)) * (np.sin((m_vec * np.pi * Width_2_Plus) / WindowWidth) - np.sin((m_vec * np.pi * Width_2_Minus) / WindowWidth)) * (Height_2_Plus - Height_2_Minus)
        A2_m0 = (mu_0 * J2_m0) / (((m_vec * np.pi) / WindowWidth)**2)
        
        sum_m0 = np.sum((A1_m0 + A2_m0) * (J1_m0 + J2_m0))

        ### Somatório em n (vetorizado)
        n_vec = np.arange(1, N, dtype=np.float64)

        J1_0n = ((2 * J_1) / (n_vec * WindowWidth * np.pi)) * (np.sin((n_vec * np.pi * Height_1_Plus) / WindowHeight) - np.sin((n_vec * np.pi * Height_1_Minus) / WindowHeight)) * (Width_1_Plus - Width_1_Minus)
        A1_0n = (mu_0 * J1_0n) / (((n_vec * np.pi) / WindowHeight)**2)
        J2_0n = ((2 * J_2) / (n_vec * WindowWidth * np.pi)) * (np.sin((n_vec * np.pi * Height_2_Plus) / WindowHeight) - np.sin((n_vec * np.pi * Height_2_Minus) / WindowHeight)) * (Width_2_Plus - Width_2_Minus)
        A2_0n = (mu_0 * J2_0n) / (((n_vec * np.pi) / WindowHeight)**2)
        
        sum_0n = np.sum((A1_0n + A2_0n) * (J1_0n + J2_0n))

        ### Somatório duplo em m e n (vetorizado com broadcasting)
        m = np.arange(1, M, dtype=np.float64)[:, np.newaxis]
        n = np.arange(1, N + 1, dtype=np.float64)
        
        term_m1 = np.sin((m * np.pi * Width_1_Plus) / WindowWidth) - np.sin((m * np.pi * Width_1_Minus) / WindowWidth)
        term_n1 = np.sin((n * np.pi * Height_1_Plus) / WindowHeight) - np.sin((n * np.pi * Height_1_Minus) / WindowHeight)
        J1_mn = ((4 * J_1) / (m * n * np.pi**2)) * term_m1 * term_n1
        
        term_m2 = np.sin((m * np.pi * Width_2_Plus) / WindowWidth) - np.sin((m * np.pi * Width_2_Minus) / WindowWidth)
        term_n2 = np.sin((n * np.pi * Height_2_Plus) / WindowHeight) - np.sin((n * np.pi * Height_2_Minus) / WindowHeight)
        J2_mn = ((4 * J_2) / (m * n * np.pi**2)) * term_m2 * term_n2

        denominator_mn = ((m * np.pi) / WindowWidth)**2 + ((n * np.pi) / WindowHeight)**2
        A1_mn = (mu_0 * J1_mn) / denominator_mn
        A2_mn = (mu_0 * J2_mn) / denominator_mn
        
        sum_mn = np.sum((A1_mn + A2_mn) * (J1_mn + J2_mn))

        ### Leakage Inductance p.u.l. (Inside Window)
        Leakage_pul_IW = ((WindowWidth * WindowHeight) / (2 * I_ref**2)) * (sum_m0 + sum_0n + 0.5 * sum_mn)

        return Leakage_pul_IW
    
    @staticmethod
    def Leakage_pul_OW_calc_vectorized(M, N, I_ref, WindowWidth, WindowHeight,
                                    NumberOfTurns_1, I_1, Width_1, Height_1, NumberOfTurns_2, I_2, Width_2, Height_2,
                                    Height_1_Minus, Height_1_Plus, Height_2_Minus, Height_2_Plus,
                                    Width_1_Minus, Width_1_Plus, Width_2_Minus, Width_2_Plus):

        mu_0 = 4 * np.pi * 1e-7
        J_1 = (NumberOfTurns_1 * I_1) / (Width_1 * Height_1)
        J_2 = (NumberOfTurns_2 * I_2) / (Width_2 * Height_2)

        # --- Parâmetros da "Janela Infinita" ---
        w_w_inf = WindowWidth * 10
        h_w_inf = WindowHeight * 10
        h_1_minus_inf = Height_1_Minus + (h_w_inf / 2 - WindowHeight / 2)
        h_1_plus_inf = Height_1_Plus + (h_w_inf / 2 - WindowHeight / 2)
        h_2_minus_inf = Height_2_Minus + (h_w_inf / 2 - WindowHeight / 2)
        h_2_plus_inf = Height_2_Plus + (h_w_inf / 2 - WindowHeight / 2)

        # --- Vetores para os índices ---
        m_vec = np.arange(1, M, dtype=np.float64)
        n_vec = np.arange(1, N, dtype=np.float64)

        # --- Somatório em m (vetorizado) ---
        J1_m0 = ((2 * J_1) / (m_vec * h_w_inf * np.pi)) * (np.sin((m_vec * np.pi * Width_1_Plus) / w_w_inf) - np.sin((m_vec * np.pi * Width_1_Minus) / w_w_inf)) * (h_1_plus_inf - h_1_minus_inf)
        A1_m0 = (mu_0 * J1_m0) / (((m_vec * np.pi) / w_w_inf)**2)
        J2_m0 = ((2 * J_2) / (m_vec * h_w_inf * np.pi)) * (np.sin((m_vec * np.pi * Width_2_Plus) / w_w_inf) - np.sin((m_vec * np.pi * Width_2_Minus) / w_w_inf)) * (h_2_plus_inf - h_2_minus_inf)
        A2_m0 = (mu_0 * J2_m0) / (((m_vec * np.pi) / w_w_inf)**2)
        sum_m0 = np.sum((A1_m0 + A2_m0) * (J1_m0 + J2_m0))

        # --- Somatório em n (vetorizado) ---
        J1_0n = ((2 * J_1) / (n_vec * w_w_inf * np.pi)) * (np.sin((n_vec * np.pi * h_1_plus_inf) / h_w_inf) - np.sin((n_vec * np.pi * h_1_minus_inf) / h_w_inf)) * (Width_1_Plus - Width_1_Minus)
        A1_0n = (mu_0 * J1_0n) / (((n_vec * np.pi) / h_w_inf)**2)
        J2_0n = ((2 * J_2) / (n_vec * w_w_inf * np.pi)) * (np.sin((n_vec * np.pi * h_2_plus_inf) / h_w_inf) - np.sin((n_vec * np.pi * h_2_minus_inf) / h_w_inf)) * (Width_2_Plus - Width_2_Minus)
        A2_0n = (mu_0 * J2_0n) / (((n_vec * np.pi) / h_w_inf)**2)
        sum_0n = np.sum((A1_0n + A2_0n) * (J1_0n + J2_0n))

        # --- Somatório duplo em m e n (vetorizado com broadcasting) ---
        m = np.arange(1, M, dtype=np.float64)[:, np.newaxis]
        n = np.arange(1, N + 1, dtype=np.float64)

        term_m1 = np.sin((m * np.pi * Width_1_Plus) / w_w_inf) - np.sin((m * np.pi * Width_1_Minus) / w_w_inf)
        term_n1 = np.sin((n * np.pi * h_1_plus_inf) / h_w_inf) - np.sin((n * np.pi * h_1_minus_inf) / h_w_inf)
        J1_mn = ((4 * J_1) / (m * n * np.pi**2)) * term_m1 * term_n1

        term_m2 = np.sin((m * np.pi * Width_2_Plus) / w_w_inf) - np.sin((m * np.pi * Width_2_Minus) / w_w_inf)
        term_n2 = np.sin((n * np.pi * h_2_plus_inf) / h_w_inf) - np.sin((n * np.pi * h_2_minus_inf) / h_w_inf)
        J2_mn = ((4 * J_2) / (m * n * np.pi**2)) * term_m2 * term_n2

        denominator_mn = ((m * np.pi) / w_w_inf)**2 + ((n * np.pi) / h_w_inf)**2
        A1_mn = (mu_0 * J1_mn) / denominator_mn
        A2_mn = (mu_0 * J2_mn) / denominator_mn
        sum_mn = np.sum((A1_mn + A2_mn) * (J1_mn + J2_mn))

        # --- Resultado Final ---
        Leakage_pul_OW = ((w_w_inf * h_w_inf) / (2 * I_ref**2)) * (sum_m0 + sum_0n + 0.5 * sum_mn)

        return Leakage_pul_OW
    
    @staticmethod
    def Leakage_pua_IW_calc_vectorized(M, N, I_ref, WindowWidth, WindowHeight, DiameterCentralLeg,
                                    NumberOfTurns_1, I_1, Width_1, Height_1, NumberOfTurns_2, I_2, Width_2, Height_2,
                                    Height_1_Minus, Height_1_Plus, Height_2_Minus, Height_2_Plus,
                                    Width_1_Minus, Width_1_Plus, Width_2_Minus, Width_2_Plus):

        mu_0 = 4 * np.pi * 1e-7
        J_1 = (NumberOfTurns_1 * I_1) / (Width_1 * Height_1)
        J_2 = (NumberOfTurns_2 * I_2) / (Width_2 * Height_2)

        # --- 1. Pré-cálculo dos termos J (substituindo os dicionários) ---
        m_range = np.arange(1, M, dtype=np.float64)
        n_range = np.arange(1, N + 1, dtype=np.float64)
        n_short_range = np.arange(1, N, dtype=np.float64)

        # J(m, 0)
        J1_m0 = ((2 * J_1) / (m_range * WindowHeight * np.pi)) * (np.sin((m_range * np.pi * Width_1_Plus) / WindowWidth) - np.sin((m_range * np.pi * Width_1_Minus) / WindowWidth)) * (Height_1_Plus - Height_1_Minus)
        J2_m0 = ((2 * J_2) / (m_range * WindowHeight * np.pi)) * (np.sin((m_range * np.pi * Width_2_Plus) / WindowWidth) - np.sin((m_range * np.pi * Width_2_Minus) / WindowWidth)) * (Height_2_Plus - Height_2_Minus)
        J_m0_vals = J1_m0 + J2_m0

        # J(0, n)
        J1_0n = ((2 * J_1) / (n_short_range * WindowWidth * np.pi)) * (np.sin((n_short_range * np.pi * Height_1_Plus) / WindowHeight) - np.sin((n_short_range * np.pi * Height_1_Minus) / WindowHeight)) * (Width_1_Plus - Width_1_Minus)
        J2_0n = ((2 * J_2) / (n_short_range * WindowWidth * np.pi)) * (np.sin((n_short_range * np.pi * Height_2_Plus) / WindowHeight) - np.sin((n_short_range * np.pi * Height_2_Minus) / WindowHeight)) * (Width_2_Plus - Width_2_Minus)
        J_0n_vals = J1_0n + J2_0n

        # J(p, n)
        p_grid_pn = m_range[:, np.newaxis]
        n_grid_pn = n_range[np.newaxis, :]
        term_p1 = np.sin((p_grid_pn * np.pi * Width_1_Plus) / WindowWidth) - np.sin((p_grid_pn * np.pi * Width_1_Minus) / WindowWidth)
        term_n1 = np.sin((n_grid_pn * np.pi * Height_1_Plus) / WindowHeight) - np.sin((n_grid_pn * np.pi * Height_1_Minus) / WindowHeight)
        J1_pn_mat = ((4 * J_1) / (p_grid_pn * n_grid_pn * np.pi**2)) * term_p1 * term_n1
        term_p2 = np.sin((p_grid_pn * np.pi * Width_2_Plus) / WindowWidth) - np.sin((p_grid_pn * np.pi * Width_2_Minus) / WindowWidth)
        term_n2 = np.sin((n_grid_pn * np.pi * Height_2_Plus) / WindowHeight) - np.sin((n_grid_pn * np.pi * Height_2_Minus) / WindowHeight)
        J2_pn_mat = ((4 * J_2) / (p_grid_pn * n_grid_pn * np.pi**2)) * term_p2 * term_n2
        J_pn_mat = J1_pn_mat + J2_pn_mat

        # --- 2. Cálculo de sum_m0 ---
        m = m_range[:, np.newaxis]
        p = m_range[np.newaxis, :]
        A_m0 = (mu_0 * J_m0_vals) / (((m_range * np.pi) / WindowWidth)**2)
        J_til_m0 = (DiameterCentralLeg / WindowWidth + 1) * J_m0_vals
        with np.errstate(divide='ignore', invalid='ignore'):
            coeff_mp = (8 / np.pi**2) * (1 / (2 * p**2) - (m**2 + p**2) / ((m**2 - p**2)**2))
        mask = (m + p) % 2 == 1
        J_til_m0_temp = np.sum(np.where(mask, coeff_mp * J_m0_vals, 0), axis=1)
        sum_m0 = np.sum(A_m0 * (J_til_m0 + J_til_m0_temp))

        # --- 3. Cálculo de sum_0n ---
        n = n_short_range[:, np.newaxis]
        A_0n = (mu_0 * J_0n_vals) / (((n_short_range * np.pi) / WindowHeight)**2)
        J_til_0n = (DiameterCentralLeg / WindowWidth + 1) * J_0n_vals
        den_pn = p**2 * WindowHeight**2 + n**2 * WindowWidth**2
        coeff_pn = (8 / np.pi**2) * (WindowHeight**2 / den_pn - (1 / p**2) * (1 + (n**2 * WindowWidth**2) / den_pn))
        J_pn_slice_0n = J_pn_mat[:, :N-1]
        mask_p_odd = p % 2 == 1
        J_til_0n_temp = 0.5 * np.sum(np.where(mask_p_odd, coeff_pn * J_pn_slice_0n.T, 0), axis=1)
        sum_0n = np.sum(A_0n * (J_til_0n + J_til_0n_temp))

        # --- 4. Cálculo de sum_mn (CORRIGIDO) ---
        m_3d = m_range[:, np.newaxis, np.newaxis]      # Shape: (M-1, 1, 1)
        n_3d = n_short_range[np.newaxis, :, np.newaxis] # Shape: (1, N-1, 1)
        p_3d = m_range[np.newaxis, np.newaxis, :]      # Shape: (1, 1, M-1)

        J_mn_mat = J_pn_mat[:, :N-1] # Esta é a matriz J(m,n) com shape (M-1, N-1)
        A_mn = (mu_0 * J_mn_mat) / (((m_range[:, np.newaxis] * np.pi) / WindowWidth)**2 + ((n_short_range[np.newaxis, :] * np.pi) / WindowHeight)**2)
        J_til_mn = (DiameterCentralLeg / WindowWidth + 1) * J_mn_mat
        
        # Preparar J(p,n) para broadcast no espaço (m,n,p)
        J_pn_for_mn_sum = J_pn_mat[:, :N-1] # Shape (p, n) -> (M-1, N-1)
        # Transpor para (n,p) e adicionar eixo 'm' para obter (1, N-1, M-1)
        J_pn_broadcastable = J_pn_for_mn_sum.T[np.newaxis, :, :]

        with np.errstate(divide='ignore', invalid='ignore'):
            den_p_n_3d = p_3d**2 * WindowHeight**2 + n_3d**2 * WindowWidth**2
            term1 = 0.5 * (WindowHeight**2 / den_p_n_3d)
            term2 = -(m_3d**2 + p_3d**2) / (m_3d**2 - p_3d**2)**2
            coeff_mnp = (8 / np.pi**2) * (term1 + term2)
        
        mask_3d = (m_3d + p_3d) % 2 == 1
        
        # Multiplicar e somar sobre o eixo 'p' (axis=2)
        J_til_mn_temp_mat = np.sum(np.where(mask_3d, coeff_mnp * J_pn_broadcastable, 0), axis=2)
        sum_mn = np.sum(A_mn * (J_til_mn + J_til_mn_temp_mat))

        # --- 5. Resultado Final ---
        Leakage_pua_IW = ((WindowHeight * (WindowWidth**2)) / (4 * I_ref**2)) * (sum_m0 + sum_0n + 0.5 * sum_mn)

        return Leakage_pua_IW
    
    @staticmethod
    def Leakage_pua_OW_calc_vectorized(M, N, I_ref, WindowWidth, WindowHeight, DiameterCentralLeg,
                                    NumberOfTurns_1, I_1, Width_1, Height_1, NumberOfTurns_2, I_2, Width_2, Height_2,
                                    Height_1_Minus, Height_1_Plus, Height_2_Minus, Height_2_Plus,
                                    Width_1_Minus, Width_1_Plus, Width_2_Minus, Width_2_Plus):

        mu_0 = 4 * np.pi * 1e-7
        J_1 = (NumberOfTurns_1 * I_1) / (Width_1 * Height_1)
        J_2 = (NumberOfTurns_2 * I_2) / (Width_2 * Height_2)

        # --- Parâmetros da "Janela Infinita" ---
        w_w_inf = WindowWidth * 10
        h_w_inf = WindowHeight * 10
        h_1_minus_inf = Height_1_Minus + (h_w_inf / 2 - WindowHeight / 2)
        h_1_plus_inf = Height_1_Plus + (h_w_inf / 2 - WindowHeight / 2)
        h_2_minus_inf = Height_2_Minus + (h_w_inf / 2 - WindowHeight / 2)
        h_2_plus_inf = Height_2_Plus + (h_w_inf / 2 - WindowHeight / 2)

        # --- 1. Pré-cálculo dos termos J ---
        m_range = np.arange(1, M, dtype=np.float64)
        n_range = np.arange(1, N + 1, dtype=np.float64)
        n_short_range = np.arange(1, N, dtype=np.float64)

        J1_m0 = ((2 * J_1) / (m_range * h_w_inf * np.pi)) * (np.sin((m_range * np.pi * Width_1_Plus) / w_w_inf) - np.sin((m_range * np.pi * Width_1_Minus) / w_w_inf)) * (h_1_plus_inf - h_1_minus_inf)
        J2_m0 = ((2 * J_2) / (m_range * h_w_inf * np.pi)) * (np.sin((m_range * np.pi * Width_2_Plus) / w_w_inf) - np.sin((m_range * np.pi * Width_2_Minus) / w_w_inf)) * (h_2_plus_inf - h_2_minus_inf)
        J_m0_vals = J1_m0 + J2_m0

        J1_0n = ((2 * J_1) / (n_short_range * w_w_inf * np.pi)) * (np.sin((n_short_range * np.pi * h_1_plus_inf) / h_w_inf) - np.sin((n_short_range * np.pi * h_1_minus_inf) / h_w_inf)) * (Width_1_Plus - Width_1_Minus)
        J2_0n = ((2 * J_2) / (n_short_range * w_w_inf * np.pi)) * (np.sin((n_short_range * np.pi * h_2_plus_inf) / h_w_inf) - np.sin((n_short_range * np.pi * h_2_minus_inf) / h_w_inf)) * (Width_2_Plus - Width_2_Minus)
        J_0n_vals = J1_0n + J2_0n

        p_grid_pn = m_range[:, np.newaxis]
        n_grid_pn = n_range[np.newaxis, :]
        term_p1 = np.sin((p_grid_pn * np.pi * Width_1_Plus) / w_w_inf) - np.sin((p_grid_pn * np.pi * Width_1_Minus) / w_w_inf)
        term_n1 = np.sin((n_grid_pn * np.pi * h_1_plus_inf) / h_w_inf) - np.sin((n_grid_pn * np.pi * h_1_minus_inf) / h_w_inf)
        J1_pn_mat = ((4 * J_1) / (p_grid_pn * n_grid_pn * np.pi**2)) * term_p1 * term_n1
        term_p2 = np.sin((p_grid_pn * np.pi * Width_2_Plus) / w_w_inf) - np.sin((p_grid_pn * np.pi * Width_2_Minus) / w_w_inf)
        term_n2 = np.sin((n_grid_pn * np.pi * h_2_plus_inf) / h_w_inf) - np.sin((n_grid_pn * np.pi * h_2_minus_inf) / h_w_inf)
        J2_pn_mat = ((4 * J_2) / (p_grid_pn * n_grid_pn * np.pi**2)) * term_p2 * term_n2
        J_pn_mat = J1_pn_mat + J2_pn_mat

        # --- 2. Cálculo de sum_m0 ---
        m = m_range[:, np.newaxis]
        p = m_range[np.newaxis, :]
        A_m0 = (mu_0 * J_m0_vals) / (((m_range * np.pi) / w_w_inf)**2)
        J_til_m0 = (DiameterCentralLeg / w_w_inf + 1) * J_m0_vals
        with np.errstate(divide='ignore', invalid='ignore'):
            coeff_mp = (8 / np.pi**2) * (1 / (2 * p**2) - (m**2 + p**2) / ((m**2 - p**2)**2))
        mask = (m + p) % 2 == 1
        J_til_m0_temp = np.sum(np.where(mask, coeff_mp * J_m0_vals, 0), axis=1)
        sum_m0 = np.sum(A_m0 * (J_til_m0 + J_til_m0_temp))

        # --- 3. Cálculo de sum_0n ---
        n = n_short_range[:, np.newaxis]
        A_0n = (mu_0 * J_0n_vals) / (((n_short_range * np.pi) / h_w_inf)**2)
        J_til_0n = (DiameterCentralLeg / w_w_inf + 1) * J_0n_vals
        den_pn = p**2 * h_w_inf**2 + n**2 * w_w_inf**2
        coeff_pn = (8 / np.pi**2) * (h_w_inf**2 / den_pn - (1 / p**2) * (1 + (n**2 * w_w_inf**2) / den_pn))
        J_pn_slice_0n = J_pn_mat[:, :N-1]
        mask_p_odd = p % 2 == 1
        J_til_0n_temp = 0.5 * np.sum(np.where(mask_p_odd, coeff_pn * J_pn_slice_0n.T, 0), axis=1)
        sum_0n = np.sum(A_0n * (J_til_0n + J_til_0n_temp))

        # --- 4. Cálculo de sum_mn ---
        m_3d = m_range[:, np.newaxis, np.newaxis]
        n_3d = n_short_range[np.newaxis, :, np.newaxis]
        p_3d = m_range[np.newaxis, np.newaxis, :]

        J_mn_mat = J_pn_mat[:, :N-1]
        A_mn = (mu_0 * J_mn_mat) / (((m_range[:, np.newaxis] * np.pi) / w_w_inf)**2 + ((n_short_range[np.newaxis, :] * np.pi) / h_w_inf)**2)
        J_til_mn = (DiameterCentralLeg / w_w_inf + 1) * J_mn_mat
        
        J_pn_for_mn_sum = J_pn_mat[:, :N-1]
        J_pn_broadcastable = J_pn_for_mn_sum.T[np.newaxis, :, :]

        with np.errstate(divide='ignore', invalid='ignore'):
            den_p_n_3d = p_3d**2 * h_w_inf**2 + n_3d**2 * w_w_inf**2
            term1 = 0.5 * (h_w_inf**2 / den_p_n_3d)
            term2 = -(m_3d**2 + p_3d**2) / (m_3d**2 - p_3d**2)**2
            coeff_mnp = (8 / np.pi**2) * (term1 + term2)
        
        mask_3d = (m_3d + p_3d) % 2 == 1
        J_til_mn_temp_mat = np.sum(np.where(mask_3d, coeff_mnp * J_pn_broadcastable, 0), axis=2)
        sum_mn = np.sum(A_mn * (J_til_mn + J_til_mn_temp_mat))

        # --- 5. Resultado Final ---
        Leakage_pua_OW = ((h_w_inf * (w_w_inf**2)) / (4 * I_ref**2)) * (sum_m0 + sum_0n + 0.5 * sum_mn)

        return Leakage_pua_OW



    def _LeakageScaler(self,
                 SelectedCore, 
                 ReferredWinding,
                 WindowWidth, WindowHeight,
                 EquivalentWindingsBlocks,
                 NumberOfTurns_1, NumberOfTurns_2):
        

        # Defines the primary and secondary windings current excitation according to the chosen reference of measurement/calculation
        match ReferredWinding:

            case "Primary":
                self.I_ref = 1
                self.I_1 = 1
                self.I_2 = -NumberOfTurns_1/NumberOfTurns_2
                
            case "Secondary":
                self.I_ref = 1
                self.I_2 = 1
                self.I_1 = -NumberOfTurns_2/NumberOfTurns_1

        

        # Defines each winding block size and position
        self.Height_1   = EquivalentWindingsBlocks['primary']['height']
        self.Width_1    = EquivalentWindingsBlocks['primary']['width']
        
        self.Height_2   = EquivalentWindingsBlocks['secondary']['height']
        self.Width_2    = EquivalentWindingsBlocks['secondary']['width']

        self.Height_1_Minus  = EquivalentWindingsBlocks['primary']['y']
        self.Height_1_Plus   = EquivalentWindingsBlocks['primary']['y'] + EquivalentWindingsBlocks['primary']['height']

        self.Height_2_Minus  = EquivalentWindingsBlocks['secondary']['y']
        self.Height_2_Plus   = EquivalentWindingsBlocks['secondary']['y'] + EquivalentWindingsBlocks['secondary']['height']

        self.Width_1_Minus   = EquivalentWindingsBlocks['primary']['x']
        self.Width_1_Plus    = EquivalentWindingsBlocks['primary']['x'] + EquivalentWindingsBlocks['primary']['width']

        self.Width_2_Minus   = EquivalentWindingsBlocks['secondary']['x']
        self.Width_2_Plus    = EquivalentWindingsBlocks['secondary']['x'] + EquivalentWindingsBlocks['secondary']['width']
        
    

        # Core-Specific Leakage Expressions
        match SelectedCore["family"]:
            
            case 'ETD':

                DiameterCentralLeg = SelectedCore["F"]
                alpha = 4*np.arctan((SelectedCore["C"]/2)/(SelectedCore["E"]/2)) # Here alpha represents the ENTIRE IW angle

                leakage_pua_IW = self.Leakage_pua_IW_calc_vectorized(30, 30, self.I_ref, WindowWidth, WindowHeight, DiameterCentralLeg, 
                                NumberOfTurns_1, self.I_1, self.Width_1, self.Height_1, NumberOfTurns_2, self.I_2, self.Width_2, self.Height_2,
                                self.Height_1_Minus, self.Height_1_Plus, self.Height_2_Minus, self.Height_2_Plus, 
                                self.Width_1_Minus, self.Width_1_Plus, self.Width_2_Minus, self.Width_2_Plus)

                leakage_pua_OW = self.Leakage_pua_OW_calc_vectorized(150, 150, self.I_ref, WindowWidth, WindowHeight, DiameterCentralLeg, 
                                NumberOfTurns_1, self.I_1, self.Width_1, self.Height_1, NumberOfTurns_2, self.I_2, self.Width_2, self.Height_2,
                                self.Height_1_Minus, self.Height_1_Plus, self.Height_2_Minus, self.Height_2_Plus, 
                                self.Width_1_Minus, self.Width_1_Plus, self.Width_2_Minus, self.Width_2_Plus)

                LeakageInductance = leakage_pua_IW*alpha + leakage_pua_OW*(2*np.pi-alpha)
    
        return LeakageInductance



















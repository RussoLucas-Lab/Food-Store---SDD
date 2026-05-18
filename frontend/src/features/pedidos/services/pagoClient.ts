/**
 * pagoClient — Cliente HTTP para la API de pagos.
 *
 * Métodos:
 * - createPago(dto) → POST /api/v1/pagos
 *
 * Notas:
 * - El token de tarjeta se genera en el browser via @mercadopago/sdk-react
 * - Los datos de tarjeta NUNCA pasan por el servidor (PCI DSS SAQ-A)
 * - El cliente solo envía el token generado por MP SDK, no los números reales
 */

import { httpClient, handleApiError } from '../../../shared/services/httpClient';

// ── Types ─────────────────────────────────────────────────────────────────────

export interface PagoCreateDTO {
  /** ID del pedido a pagar */
  pedido_id: number;
  /** Token de tarjeta generado por MercadoPago SDK en el browser */
  token: string;
  /** Número de cuotas (1 = sin cuotas) */
  installments: number;
  /** ID del método de pago (ej: visa, master, amex) */
  payment_method_id: string;
  /** ID del banco emisor (opcional) */
  issuer_id?: string;
}

export interface PagoResponse {
  id: number;
  pedido_id: number;
  mp_payment_id: string | null;
  mp_status: string;
  creado_en: string;
}

// ── Base URL ──────────────────────────────────────────────────────────────────

const BASE = '/api/v1/pagos';

// ── API calls ─────────────────────────────────────────────────────────────────

/**
 * Crear un pago para el pedido usando MercadoPago.
 * POST /api/v1/pagos
 *
 * @param dto Datos del pago (token de tarjeta generado por MP SDK, pedido_id, etc.)
 * @returns Respuesta con el pago creado
 *
 * @example
 * const pago = await createPago({
 *   pedido_id: 42,
 *   token: mpCardToken,         // generado por MP SDK en browser
 *   installments: 1,
 *   payment_method_id: 'visa',
 * });
 */
export async function createPago(dto: PagoCreateDTO): Promise<PagoResponse> {
  try {
    const response = await httpClient.post<PagoResponse>(BASE, dto);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
}

const pagoClient = {
  createPago,
};

export default pagoClient;

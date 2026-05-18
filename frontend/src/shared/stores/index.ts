/**
 * Shared Stores — Exports centralizados
 */

export { useCartStore, getSnapshot as getCartSnapshot } from './cartStore';
export type { CartItem, CartCreateDTO, CartStore } from './cartStore';

export { useUiStore, getUiSnapshot } from './uiStore';
export type { UiStore, ConfirmModal } from './uiStore';

export { useAuthStore, getSnapshot as getAuthSnapshot } from './authStore';
export type { AuthState } from './authStore';

export { usePaymentStore, getSnapshot as getPaymentSnapshot } from './paymentStore';
export type { PaymentState } from './paymentStore';

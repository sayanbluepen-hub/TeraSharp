/**
 * mockValidationData.js
 *
 * All demo/mock data for the SRM Validation Dashboard.
 * Replace these values with real API responses from Sayan's FastAPI endpoint.
 *
 * Expected future API shape:
 * {
 *   overall_accuracy: number,       // 0–100
 *   kappa: number,                  // 0–1
 *   confusion_matrix: number[][],   // 5x5
 *   pixel: {
 *     built_up: number,             // 0–1 fraction
 *     vegetation: number,
 *     water: number,
 *     cropland: number,
 *     bare_land: number,
 *     entropy: number,
 *     B04: number,
 *     B03: number,
 *     B02: number,
 *     B08: number,
 *   },
 *   baseline: {
 *     nearest_neighbor: { overall_accuracy: number, kappa: number },
 *     srm_model:        { overall_accuracy: number, kappa: number },
 *   }
 * }
 */

// ─── Model Validation ────────────────────────────────────────────────────────
export const VALIDATION_METRICS = {
  overall_accuracy: 91.8,
  kappa: 0.87,
};

// ─── Confusion Matrix ─────────────────────────────────────────────────────────
export const CLASS_LABELS = [
  'Built-up',
  'Vegetation',
  'Water',
  'Cropland',
  'Bare Land',
];

// Rows = Actual, Columns = Predicted
export const CONFUSION_MATRIX = [
  [92, 4, 1, 2, 1],
  [3, 91, 2, 3, 1],
  [1, 2, 95, 1, 1],
  [3, 4, 1, 89, 3],
  [2, 2, 1, 4, 91],
];

// ─── Sub-Pixel Inspector ──────────────────────────────────────────────────────
export const MOCK_PIXEL_DATA = {
  built_up:   0.72,
  vegetation: 0.10,
  water:      0.03,
  cropland:   0.08,
  bare_land:  0.07,
  entropy:    0.21,
  B04: 1240,
  B03:  980,
  B02:  760,
  B08: 2310,
};

// ─── Baseline Comparison ──────────────────────────────────────────────────────
export const BASELINE_DATA = {
  nearest_neighbor: {
    overall_accuracy: 72.4,
    kappa: 0.61,
  },
  srm_model: {
    overall_accuracy: 91.8,
    kappa: 0.87,
  },
};

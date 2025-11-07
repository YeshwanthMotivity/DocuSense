/**
 * Reports web vitals metrics.
 *
 * @param {function(import('web-vitals').Metric): void} onPerfEntry A callback function
 *   that will be called with each web vital metric (e.g., CLS, FID, FCP, LCP, TTFB).
 *   The function is expected to receive a Metric object from the 'web-vitals' library.
 */
const reportWebVitals = onPerfEntry => {
  if (onPerfEntry && typeof onPerfEntry === 'function') {
    import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      getCLS(onPerfEntry);
      getFID(onPerfEntry);
      getFCP(onPerfEntry);
      getLCP(onPerfEntry);
      getTTFB(onPerfEntry);
    });
  }
};

export default reportWebVitals;
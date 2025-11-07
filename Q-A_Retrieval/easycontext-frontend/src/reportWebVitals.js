const reportWebVitals = onPerfEntry => {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    import('web-vitals').then(webVitals => {
      const metrics = [
        webVitals.getCLS,
        webVitals.getFID,
        webVitals.getFCP,
        webVitals.getLCP,
        webVitals.getTTFB,
      ];
      metrics.forEach(metricFn => metricFn(onPerfEntry));
    });
  }
};

export default reportWebVitals;
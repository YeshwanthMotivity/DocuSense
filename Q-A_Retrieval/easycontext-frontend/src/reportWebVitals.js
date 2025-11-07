const reportWebVitals = onPerfEntry => {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      const vitalsFunctions = [getCLS, getFID, getFCP, getLCP, getTTFB];
      vitalsFunctions.forEach(func => func(onPerfEntry));
    });
  }
};

export default reportWebVitals;
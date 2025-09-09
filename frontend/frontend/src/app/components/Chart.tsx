"use client";

import React, { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';

interface ChartProps {
  chartData: {
    chart_type: string;
    title: string;
    data: any;
  };
}

const ChartComponent: React.FC<ChartProps> = ({ chartData }) => {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstance = useRef<Chart | null>(null);

  useEffect(() => {
    if (chartRef.current) {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
      const ctx = chartRef.current.getContext('2d');
      if (ctx) {
        chartInstance.current = new Chart(ctx, {
          type: chartData.chart_type as any,
          data: chartData.data,
          options: {
            responsive: true,
            plugins: {
              legend: {
                position: 'top',
              },
              title: {
                display: true,
                text: chartData.title,
              },
            },
          },
        });
      }
    }

    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, [chartData]);

  return <canvas ref={chartRef} />;
};

export default ChartComponent;

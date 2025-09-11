"use client";

import React, { useState, useRef } from 'react';
import ChartComponent from './Chart';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

interface ReportProps {
  report: {
    report_id: string;
    url: string;
    generated_at: string;
    summary: string;
    sections: {
      title: string;
      content: string;
      charts: {
        chart_type: string;
        title: string;
        data: any;
      }[];
    }[];
  };
}

const Report: React.FC<ReportProps> = ({ report }) => {
  const [openSections, setOpenSections] = useState<string[]>(report.sections.map(s => s.title));
  const reportRef = useRef<HTMLDivElement>(null);

  const toggleSection = (title: string) => {
    if (openSections.includes(title)) {
      setOpenSections(openSections.filter(s => s !== title));
    } else {
      setOpenSections([...openSections, title]);
    }
  };

  const exportToJson = () => {
    const jsonString = `data:text/json;charset=utf-8,${encodeURIComponent(
      JSON.stringify(report, null, 2)
    )}`;
    const link = document.createElement('a');
    link.href = jsonString;
    link.download = `report-${report.report_id}.json`;
    link.click();
  };

  const exportToPdf = () => {
    if (reportRef.current) {
      html2canvas(reportRef.current).then(canvas => {
        const imgData = canvas.toDataURL('image/png');
        const pdf = new jsPDF('p', 'mm', 'a4');
        const pdfWidth = pdf.internal.pageSize.getWidth();
        const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
        pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
        pdf.save(`report-${report.report_id}.pdf`);
      });
    }
  };

  return (
    <div className="mt-8 w-full max-w-4xl p-4 bg-white shadow-lg rounded-lg" ref={reportRef}>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">Analysis Report for {report.url}</h2>
        <div>
          <button onClick={exportToJson} className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mr-2">
            Export to JSON
          </button>
          <button onClick={exportToPdf} className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">
            Export to PDF
          </button>
        </div>
      </div>
      <p className="text-sm text-gray-500 mb-4">Generated at: {new Date(report.generated_at).toLocaleString()}</p>

      <div className="mb-4 p-4 bg-gray-100 rounded">
        <h3 className="text-xl font-semibold">Summary</h3>
        <p>{report.summary}</p>
      </div>

      <div>
        {report.sections.map(section => (
          <div key={section.title} className="mb-4 border rounded">
            <button
              className="w-full text-left p-4 bg-gray-200 hover:bg-gray-300 focus:outline-none"
              onClick={() => toggleSection(section.title)}
            >
              <h3 className="text-xl font-semibold">{section.title}</h3>
            </button>
            {openSections.includes(section.title) && (
              <div className="p-4">
                <p className="mb-4">{section.content}</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {section.charts.map(chart => (
                    <div key={chart.title}>
                      <ChartComponent chartData={chart} />
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Report;

import type { RiskPredictionResponse, StudentRiskRequest } from '../core/services/xaiService';

/**
 * Export prediction report as PDF
 * Opens a print dialog with formatted report
 */
export function exportPredictionToPDF(
  prediction: RiskPredictionResponse,
  formData: StudentRiskRequest,
  actionPlan: any[]
) {
  const printWindow = window.open('', '_blank');
  if (!printWindow) return;

  printWindow.document.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>Academic Risk Report - ${formData.student_id}</title>
        <style>
          * { margin: 0; padding: 0; box-sizing: border-box; }
          body { font-family: Arial, sans-serif; padding: 40px; color: #333; }
          .header { text-align: center; margin-bottom: 40px; border-bottom: 3px solid #667eea; padding-bottom: 20px; }
          .header h1 { color: #667eea; font-size: 28px; margin-bottom: 10px; }
          .risk-badge { display: inline-block; padding: 10px 20px; border-radius: 8px; font-weight: bold; margin: 20px 0; }
          .risk-safe { background: #d1fae5; color: #065f46; }
          .risk-medium { background: #fef3c7; color: #92400e; }
          .risk-high { background: #fee2e2; color: #991b1b; }
          .section { margin: 30px 0; }
          .section h2 { color: #667eea; margin-bottom: 15px; font-size: 20px; }
          .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0; }
          .info-item { background: #f3f4f6; padding: 15px; border-radius: 8px; }
          .info-label { font-weight: bold; color: #4b5563; font-size: 12px; margin-bottom: 5px; }
          .info-value { font-size: 18px; color: #111827; }
          .action-item { background: #f9fafb; padding: 15px; margin: 10px 0; border-left: 4px solid #667eea; border-radius: 4px; }
          .action-title { font-weight: bold; margin-bottom: 5px; }
          .priority { display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; margin-right: 10px; }
          .priority-critical { background: #fee2e2; color: #991b1b; }
          .priority-high { background: #fef3c7; color: #92400e; }
          .priority-medium { background: #dbeafe; color: #1e40af; }
          .priority-standard { background: #d1fae5; color: #065f46; }
          .footer { margin-top: 50px; text-align: center; color: #6b7280; font-size: 12px; border-top: 1px solid #e5e7eb; padding-top: 20px; }
          @media print { body { padding: 20px; } }
        </style>
      </head>
      <body>
        <div class="header">
          <h1>🎓 Academic Risk Assessment Report</h1>
          <p>Student ID: <strong>${formData.student_id}</strong></p>
          <p>Generated: ${new Date().toLocaleDateString()} ${new Date().toLocaleTimeString()}</p>
        </div>
        
        <div class="section">
          <h2>Risk Assessment</h2>
          <div class="risk-badge risk-${prediction.risk_level === 'Safe' ? 'safe' : prediction.risk_level === 'Medium Risk' ? 'medium' : 'high'}">
            ${prediction.risk_level} - ${prediction.confidence.toFixed(2)}% Prediction Certainty
          </div>
          <p><strong>Risk Score:</strong> ${(prediction.risk_score * 100).toFixed(2)}%</p>
        </div>

        <div class="section">
          <h2>Student Metrics</h2>
          <div class="info-grid">
            <div class="info-item"><div class="info-label">Average Grade</div><div class="info-value">${formData.avg_grade}%</div></div>
            <div class="info-item"><div class="info-label">Grade Consistency</div><div class="info-value">${formData.grade_consistency}%</div></div>
            <div class="info-item"><div class="info-label">Assessments Completed</div><div class="info-value">${formData.num_assessments}</div></div>
            <div class="info-item"><div class="info-label">Completion Rate</div><div class="info-value">${(formData.assessment_completion_rate * 100).toFixed(0)}%</div></div>
            <div class="info-item"><div class="info-label">Credits Studied</div><div class="info-value">${formData.studied_credits}</div></div>
            <div class="info-item"><div class="info-label">Previous Attempts</div><div class="info-value">${formData.num_of_prev_attempts}</div></div>
          </div>
        </div>

        <div class="section">
          <h2>Personalized Action Plan (${actionPlan.length} items)</h2>
          ${actionPlan.map((action, idx) => `
            <div class="action-item">
              <div class="action-title">
                <span class="priority priority-${action.priority}">${action.priority.toUpperCase()}</span>
                ${idx + 1}. ${action.title}
              </div>
              <p>${action.description}</p>
              <small style="color: #6b7280;">Category: ${action.category.replace('-', ' ')}</small>
            </div>
          `).join('')}
        </div>

        <div class="footer">
          <p><strong>EduMind Academic Risk Prediction System</strong></p>
          <p>Powered by XGBoost ML Model | Generated on ${new Date().toLocaleDateString()}</p>
        </div>
      </body>
      </html>
    `);

  printWindow.document.close();
  setTimeout(() => {
    printWindow.print();
  }, 250);
}

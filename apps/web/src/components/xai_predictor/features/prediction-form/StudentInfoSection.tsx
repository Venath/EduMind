import { ConnectedStudentSearchSection } from './ConnectedStudentSearchSection';
import type { StudentInfoSectionProps } from './types';

export function StudentInfoSection({
    isAnalyzingConnectedStudent,
    onAnalyzeConnectedStudent,
    prefilledStudentId,
}: StudentInfoSectionProps) {
    return (
        <div className="space-y-4">
            <ConnectedStudentSearchSection
                isAnalyzing={isAnalyzingConnectedStudent}
                onAnalyzeStudent={onAnalyzeConnectedStudent}
                prefilledStudentId={prefilledStudentId}
            />
        </div>
    );
}

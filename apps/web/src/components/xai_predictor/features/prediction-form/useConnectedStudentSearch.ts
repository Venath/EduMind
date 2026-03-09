import { useEffect, useState } from 'react';
import { xaiService, type ConnectedStudentSummary } from '../../core/services/xaiService';

type UseConnectedStudentSearchOptions = {
    instituteId: string;
    prefilledStudentId?: string;
    onPrefillStudentId: (studentId: string) => void;
};

export function useConnectedStudentSearch({
    instituteId,
    prefilledStudentId,
    onPrefillStudentId,
}: UseConnectedStudentSearchOptions) {
    const [query, setQuery] = useState(prefilledStudentId ?? '');
    const [results, setResults] = useState<ConnectedStudentSummary[]>([]);
    const [isSearching, setIsSearching] = useState(false);
    const [hasSearched, setHasSearched] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const searchStudents = async (nextQuery?: string) => {
        const searchQuery = (nextQuery ?? query).trim();
        if (!searchQuery) {
            setResults([]);
            setHasSearched(true);
            setError(null);
            return;
        }

        setIsSearching(true);
        setHasSearched(true);
        setError(null);

        try {
            const response = await xaiService.searchStudents(searchQuery, {
                limit: 8,
                instituteId,
            });
            setResults(response.students);
        } catch (searchError) {
            const message =
                searchError instanceof Error
                    ? searchError.message
                    : 'Student search failed';
            setError(message);
            setResults([]);
        } finally {
            setIsSearching(false);
        }
    };

    useEffect(() => {
        if (!prefilledStudentId) {
            return;
        }

        setQuery(prefilledStudentId);
        onPrefillStudentId(prefilledStudentId);
        void searchStudents(prefilledStudentId);
        // Triggered only when a route-scoped student prefill changes.
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [prefilledStudentId, instituteId]);

    return {
        query,
        setQuery,
        results,
        isSearching,
        hasSearched,
        error,
        searchStudents,
    };
}

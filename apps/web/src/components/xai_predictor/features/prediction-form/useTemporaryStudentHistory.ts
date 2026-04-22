import { useEffect, useMemo, useRef, useState } from 'react';
import { xaiService, type TemporaryStudentSummary } from '../../core/services/xaiService';

type UseTemporaryStudentHistoryOptions = {
    refreshToken: number;
};

export function useTemporaryStudentHistory({
    refreshToken,
}: UseTemporaryStudentHistoryOptions) {
    const [query, setQuery] = useState('');
    const queryRef = useRef('');
    const [records, setRecords] = useState<TemporaryStudentSummary[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [hasLoaded, setHasLoaded] = useState(false);

    const updateQuery = (value: string) => {
        queryRef.current = value;
        setQuery(value);
    };

    const totalLabel = useMemo(() => {
        if (!hasLoaded) {
            return 'Saved records';
        }

        return `${records.length} saved record${records.length === 1 ? '' : 's'}`;
    }, [hasLoaded, records.length]);

    const loadRecords = async (nextQuery?: string) => {
        const searchQuery = (nextQuery ?? queryRef.current).trim();
        setIsLoading(true);
        setError(null);

        try {
            const response = await xaiService.getTemporaryStudents({
                query: searchQuery,
                limit: 8,
            });
            setRecords(response.students);
            setHasLoaded(true);
        } catch (loadError) {
            const message =
                loadError instanceof Error
                    ? loadError.message
                    : 'Could not load temporary students';
            setError(message);
            setRecords([]);
            setHasLoaded(true);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        void loadRecords();
        // Refresh list after the temporary-student flow persists a new record.
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [refreshToken]);

    return {
        query,
        setQuery: updateQuery,
        records,
        isLoading,
        error,
        hasLoaded,
        totalLabel,
        loadRecords,
    };
}

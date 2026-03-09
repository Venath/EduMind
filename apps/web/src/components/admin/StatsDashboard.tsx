import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BookOpen, CheckCircle, FileText, Users } from 'lucide-react';

interface StatsDashboardProps {
    stats: {
        students: number;
        courses: number;
        resources: number;
        averagePerformance: number;
    };
}

export function StatsDashboard({ stats }: StatsDashboardProps) {
    const statItems = [
        {
            title: "Total Students",
            value: stats.students.toLocaleString(),
            icon: Users,
            color: "text-purple-600",
            bg: "bg-purple-100 dark:bg-purple-900/20"
        },
        {
            title: "Active Courses",
            value: stats.courses,
            icon: BookOpen,
            color: "text-blue-600",
            bg: "bg-blue-100 dark:bg-blue-900/20"
        },
        {
            title: "Learning Resources",
            value: stats.resources.toLocaleString(),
            icon: FileText,
            color: "text-emerald-600",
            bg: "bg-emerald-100 dark:bg-emerald-900/20"
        },
        {
            title: "Average Performance",
            value: `${stats.averagePerformance}%`,
            icon: CheckCircle,
            color: "text-orange-600",
            bg: "bg-orange-100 dark:bg-orange-900/20"
        }
    ];

    return (
        <section id="dashboard" className="py-12 bg-background/50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {statItems.map((item, index) => (
                        <Card key={index} className="border-border hover:shadow-lg transition-all duration-300">
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium text-muted-foreground">
                                    {item.title}
                                </CardTitle>
                                <div className={`p-2 rounded-full ${item.bg}`}>
                                    <item.icon className={`h-4 w-4 ${item.color}`} />
                                </div>
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{item.value}</div>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            </div>
        </section>
    );
}

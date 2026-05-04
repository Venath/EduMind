import { Sliders } from 'lucide-react';

export function ScenarioIntro() {
    return (
        <div className="bg-muted/30 p-4 rounded-lg flex gap-4 items-start border border-border/50">
            <div className="bg-cyan-100 p-2 rounded-full">
                <Sliders size={24} className="text-cyan-600" />
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed">
                Apply a realistic intervention preset or adjust metrics manually to estimate how the
                student&apos;s predicted risk could shift. This simulation highlights which changes
                have the strongest projected impact before any real-world intervention is made.
            </p>
        </div>
    );
}

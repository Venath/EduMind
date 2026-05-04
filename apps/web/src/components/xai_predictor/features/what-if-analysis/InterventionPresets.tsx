import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Sparkles } from 'lucide-react';
import type { InterventionPresetsProps } from './types';

export function InterventionPresets({
    presets,
    selectedPresetId,
    onApplyPreset,
}: InterventionPresetsProps) {
    return (
        <Card className="border shadow-sm">
            <CardHeader className="border-b bg-muted/30 pb-4">
                <h3 className="flex items-center gap-2 text-lg font-bold">
                    <Sparkles size={18} className="text-primary" />
                    Intervention Impact Simulator
                </h3>
                <p className="text-sm text-muted-foreground">
                    Apply a realistic support scenario, then simulate its projected effect on
                    student risk.
                </p>
            </CardHeader>
            <CardContent className="grid gap-3 p-4 md:grid-cols-2">
                {presets.map((preset) => {
                    const isSelected = preset.id === selectedPresetId;
                    return (
                        <div
                            key={preset.id}
                            className={`rounded-2xl border p-4 text-left transition-all ${
                                isSelected
                                    ? 'border-primary bg-primary/5 shadow-sm ring-1 ring-primary/20'
                                    : 'border-border/60 bg-background hover:border-primary/40 hover:bg-muted/20'
                            }`}
                        >
                            <div className="flex items-start justify-between gap-3">
                                <div>
                                    <h4 className="text-sm font-semibold text-foreground">
                                        {preset.title}
                                    </h4>
                                    <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                                        {preset.description}
                                    </p>
                                </div>
                                <Button
                                    type="button"
                                    onClick={() => onApplyPreset(preset.id)}
                                    variant={isSelected ? 'default' : 'outline'}
                                    size="sm"
                                    className="shrink-0"
                                >
                                    {isSelected ? 'Selected' : 'Apply'}
                                </Button>
                            </div>
                            <p className="mt-3 rounded-xl bg-muted/40 px-3 py-2 text-xs leading-relaxed text-muted-foreground">
                                {preset.expectedImpact}
                            </p>
                        </div>
                    );
                })}
            </CardContent>
        </Card>
    );
}

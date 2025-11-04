"use client";

interface StatCardProps {
  icon: string;
  label: string;
  value: string | number;
  subtext?: string;
  color?: "blue" | "green" | "orange" | "red" | "purple";
}

export default function AdminStatsCard({
  icon,
  label,
  value,
  subtext,
  color = "blue",
}: StatCardProps) {
  const colorClasses: Record<string, string> = {
    blue: "border-blue-200 bg-blue-50",
    green: "border-green-200 bg-green-50",
    orange: "border-orange-200 bg-orange-50",
    red: "border-red-200 bg-red-50",
    purple: "border-purple-200 bg-purple-50",
  };

  const textColorClasses: Record<string, string> = {
    blue: "text-blue-600",
    green: "text-green-600",
    orange: "text-orange-600",
    red: "text-red-600",
    purple: "text-purple-600",
  };

  return (
    <div
      className={`rounded-lg border-2 p-4 ${colorClasses[color]}`}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-600 mb-1">{label}</p>
          <p className={`text-2xl font-bold ${textColorClasses[color]}`}>
            {value}
          </p>
          {subtext && (
            <p className="text-xs text-gray-500 mt-1">{subtext}</p>
          )}
        </div>
        <span className="text-3xl">{icon}</span>
      </div>
    </div>
  );
}

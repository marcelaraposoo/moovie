interface RatingBadgeProps {
  value: number; // escala 0-10
  size?: "sm" | "lg";
}

export default function RatingBadge({ value, size = "sm" }: RatingBadgeProps) {
  return (
    <span className={`rating-badge-circle rating-badge-${size}`} aria-label={`Nota ${value.toFixed(1)} de 10`}>
      {value.toFixed(1)}
    </span>
  );
}

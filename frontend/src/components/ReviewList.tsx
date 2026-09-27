import type { Review } from "../types/movie";
import RatingBadge from "./RatingBadge";

interface ReviewListProps {
  reviews: Review[];
}

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString("pt-BR", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    });
  } catch {
    return iso;
  }
}

export default function ReviewList({ reviews }: ReviewListProps) {
  if (reviews.length === 0) {
    return <p className="empty-state">Ainda não há avaliações para este filme. Seja o primeiro a avaliar!</p>;
  }

  return (
    <ul className="review-list">
      {reviews.map((review) => (
        <li key={review.sk_movie_review_id} className="review-item">
          <div className="review-item-header">
            <RatingBadge value={review.nota} />
            <strong>{review.nome}</strong>
            <span className="review-date">{formatDate(review.created_at)}</span>
          </div>
          <p className="review-comment">{review.comentario}</p>
        </li>
      ))}
    </ul>
  );
}

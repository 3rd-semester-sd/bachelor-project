import { z } from "zod";

export const restaurantMemberDTO = z.object({
  member_id: z.string().uuid(),
  name: z.string(),
  email: z.string().email(),
});
export const restaurantMemberRequestDTO = restaurantMemberDTO.omit({
  member_id: true,
});

export type RestaurantMember = z.infer<typeof restaurantMemberDTO>;

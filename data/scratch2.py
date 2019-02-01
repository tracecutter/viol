
        clist = [
            [self.outline_feature_centerline.top_left, self.outline_feature_45_upper_left],
            [self.outline_feature_turn_upper_left, self.outline_feature_45_upper_left],
            [self.outline_feature_turn_upper_left, self.outline_feature_corner_upper_left],
            [self.outline_feature_bout_middle.left, self.outline_feature_corner_upper_left],
            [self.outline_feature_bout_middle.left, self.outline_feature_corner_lower_left],
            [self.outline_feature_turn_lower_left, self.outline_feature_corner_lower_left],
            [self.outline_feature_turn_lower_left, self.outline_feature_45_lower_left],
            [self.outline_feature_centerline.bot, self.outline_feature_45_lower_left],
            [self.outline_feature_centerline.bot, self.outline_feature_45_lower_right],
            [self.outline_feature_turn_lower_right, self.outline_feature_45_lower_right],
            [self.outline_feature_turn_lower_right, self.outline_feature_corner_lower_right],
            [self.outline_feature_bout_middle.right, self.outline_feature_corner_lower_right],
            [self.outline_feature_bout_middle.right, self.outline_feature_corner_upper_right],
            [self.outline_feature_turn_upper_right, self.outline_feature_corner_upper_right],
            [self.outline_feature_turn_upper_right, self.outline_feature_45_upper_right],
            [self.outline_feature_centerline.top_right, self.outline_feature_45_upper_right]
        ]

        # iterate over every clothoid to construct
        for points in clist:
            p0,p1 = [points[0].p(),points[1].p()] 
            # calculate transform based on entry angle and cw/ccw twist
            scale, rotation, hflip, vflip = twist_calc(p0,p1)

        # calculate the scale
        arclen = self.outline_path.length(T0=0, T1=self.outline_feature_45_upper_left.T)
        scale = (arclen/math.sqrt(0.5)) * 1.0875
        
        # calculate delta phi
        phi = phase_delta_min(phi_p0,phi_p1)
        delta_t = math.sqrt(((0 + phi) * 2)/cmath.pi)

            for i in range(0,10):
                cl = Clothoid(scale, rotation, (p0.x(),p0.y()), hflip, vflip)
                t = cl.closest_t(p1)
                ph1 = cmath.phase(p1 - p0)
                ph2 = cmath.phase(cl.p(t) - p0)
                #print "p1:", p1
                #print "t, p(t):", t, cl.p(t)
                #print "ph1, ph2, delta, min_delta_degrees:", ph1, ph2, ph1 - ph2, phase_delta_min(ph1, ph2)
                #print "rotation", rotation, math.degrees(rotation)
                self.outline_guesses.append(Point(cl.x(t),cl.y(t)))
                self.outline_clothoids.append(cl)
                rotation = rotation + (ph1 - ph2)

            path_compare(self.outline_path, 0.0, self.outline_feature_45_upper_left.T, cl, 0.0, t, nodes=10)

            self.outline_clothoids.append(cl)

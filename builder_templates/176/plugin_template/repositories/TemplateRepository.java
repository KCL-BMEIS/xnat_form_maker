/*
 * xnat-template: org.nrg.xnat.plugins.template.repositories.TemplateRepository
 * XNAT http://www.xnat.org
 * Copyright (c) 2017, Washington University School of Medicine
 * All Rights Reserved
 *
 * Released under the Simplified BSD.
 */

package org.nrg.xnat.plugins.[HERE_SCHEMANAME_LOWER].repositories;

import org.nrg.framework.orm.hibernate.AbstractHibernateDAO;
import org.nrg.xnat.plugins.[HERE_SCHEMANAME_LOWER].entities.[HERE_SCHEMANAME];
import org.springframework.stereotype.Repository;

@Repository
public class [HERE_SCHEMANAME]Repository extends AbstractHibernateDAO<[HERE_SCHEMANAME]> {
}
